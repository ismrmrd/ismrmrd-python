import sys
import argparse
import numpy as np
from typing import BinaryIO, Iterable, Union

from ismrmrd import Acquisition, Image, ImageHeader, ProtocolDeserializer, ProtocolSerializer
from ismrmrd.xsd import ismrmrdHeader
from ismrmrd.constants import ACQ_IS_NOISE_MEASUREMENT, IMTYPE_MAGNITUDE
from ismrmrd.serialization import SerializableObject

from numpy.fft import fftshift, ifftshift, fftn, ifftn


def kspace_to_image(k: np.ndarray, dim=None, img_shape=None) -> np.ndarray:
    """ Computes the Fourier transform from k-space to image space
    along a given or all dimensions

    :param k: k-space data
    :param dim: vector of dimensions to transform
    :param img_shape: desired shape of output image
    :returns: data in image space (along transformed dimensions)
    """
    if not dim:
        dim = range(k.ndim)
    img = fftshift(ifftn(ifftshift(k, axes=dim), s=img_shape, axes=dim), axes=dim)
    img *= np.sqrt(np.prod(np.take(img.shape, dim)))
    return img


def image_to_kspace(img: np.ndarray, dim=None, k_shape=None) -> np.ndarray:
    """ Computes the Fourier transform from image space to k-space space
    along a given or all dimensions

    :param img: image space data
    :param dim: vector of dimensions to transform
    :param k_shape: desired shape of output k-space data
    :returns: data in k-space (along transformed dimensions)
    """
    if not dim:
        dim = range(img.ndim)
    k = fftshift(fftn(ifftshift(img, axes=dim), s=k_shape, axes=dim), axes=dim)
    k /= np.sqrt(np.prod(np.take(img.shape, dim)))
    return k


def acquisition_reader(input: Iterable[SerializableObject]) -> Iterable[Acquisition]:
    for item in input:
        if not isinstance(item, Acquisition):
            # Skip non-acquisition items
            continue
        if item.flags & ACQ_IS_NOISE_MEASUREMENT:
            # Currently ignoring noise scans
            continue
        yield item

def stream_item_sink(input: Iterable[Union[Acquisition, Image]]) -> Iterable[SerializableObject]:
    for item in input:
        if isinstance(item, Acquisition):
            yield item
        elif isinstance(item, Image) and item.data.dtype == np.float32:
            yield item
        else:
            raise ValueError("Unknown item type")

def remove_oversampling(head: ismrmrdHeader, input: Iterable[Acquisition]) -> Iterable[Acquisition]:
    enc = head.encoding[0]

    if enc.encodedSpace and enc.encodedSpace.matrixSize and enc.reconSpace and enc.reconSpace.matrixSize:
        eNx = enc.encodedSpace.matrixSize.x
        rNx = enc.reconSpace.matrixSize.x
    else:
        raise Exception('Encoding information missing from header')

    for acq in input:
        if eNx != rNx and acq.number_of_samples == eNx:
            xline = kspace_to_image(acq.data, [1])
            x0 = (eNx - rNx) // 2
            x1 = x0 + rNx
            xline = xline[:, x0:x1]
            head = acq.getHead()
            head.center_sample = rNx // 2
            data = image_to_kspace(xline, [1])
            acq = Acquisition(head, data)
        yield acq

def accumulate_fft(head: ismrmrdHeader, input: Iterable[Acquisition]) -> Iterable[Image]:
    enc = head.encoding[0]

    # Matrix size
    if enc.encodedSpace and enc.reconSpace and enc.encodedSpace.matrixSize and enc.reconSpace.matrixSize:
        eNx = enc.encodedSpace.matrixSize.x
        eNy = enc.encodedSpace.matrixSize.y
        eNz = enc.encodedSpace.matrixSize.z
        rNx = enc.reconSpace.matrixSize.x
        rNy = enc.reconSpace.matrixSize.y
        rNz = enc.reconSpace.matrixSize.z
    else:
        raise Exception('Required encoding information not found in header')

    # Field of view
    if enc.reconSpace and enc.reconSpace.fieldOfView_mm:
        rFOVx = enc.reconSpace.fieldOfView_mm.x
        rFOVy = enc.reconSpace.fieldOfView_mm.y
        rFOVz = enc.reconSpace.fieldOfView_mm.z if enc.reconSpace.fieldOfView_mm.z else 1
    else:
        raise Exception('Required field of view information not found in header')

    # Number of Slices, Reps, Contrasts, etc.
    ncoils = 1
    if head.acquisitionSystemInformation and head.acquisitionSystemInformation.receiverChannels:
        ncoils = head.acquisitionSystemInformation.receiverChannels

    nslices = 1
    if enc.encodingLimits and enc.encodingLimits.slice != None:
        nslices = enc.encodingLimits.slice.maximum + 1

    ncontrasts = 1
    if enc.encodingLimits and enc.encodingLimits.contrast != None:
        ncontrasts = enc.encodingLimits.contrast.maximum + 1

    ky_offset = 0
    if enc.encodingLimits and enc.encodingLimits.kspace_encoding_step_1 != None:
        ky_offset = int((eNy+1)/2) - enc.encodingLimits.kspace_encoding_step_1.center

    current_rep = -1
    reference_acquisition = None
    buffer = None
    image_index = 0

    def produce_image(buffer: np.ndarray, ref_acq: Acquisition) -> Iterable[Image]:
        nonlocal image_index

        if buffer.shape[-3] > 1:
            img = kspace_to_image(buffer, dim=[-1, -2, -3])
        else:
            img = kspace_to_image(buffer, dim=[-1, -2])

        for contrast in range(img.shape[0]):
            for islice in range(img.shape[1]):
                slice = img[contrast, islice]
                combined = np.squeeze(np.sqrt(np.abs(np.sum(slice * np.conj(slice), axis=0)).astype('float32')))

                xoffset = (combined.shape[-1] + 1) // 2 - (rNx+1) // 2
                yoffset = (combined.shape[-2] + 1) // 2 - (rNy+1) // 2
                if len(combined.shape) == 3:
                    zoffset = (combined.shape[-3] + 1) // 2 - (rNz+1) // 2
                    combined = combined[zoffset:(zoffset+rNz), yoffset:(yoffset+rNy), xoffset:(xoffset+rNx)]
                    combined = np.reshape(combined, (1, combined.shape[-3], combined.shape[-2], combined.shape[-1]))
                elif len(combined.shape) == 2:
                    combined = combined[yoffset:(yoffset+rNy), xoffset:(xoffset+rNx)]
                    combined = np.reshape(combined, (1, 1, combined.shape[-2], combined.shape[-1]))
                else:
                    raise Exception('Array img_combined should have 2 or 3 dimensions')

                imghdr = ImageHeader(image_type=IMTYPE_MAGNITUDE)
                imghdr.version = 1
                imghdr.measurement_uid = ref_acq.measurement_uid
                imghdr.field_of_view[0] = rFOVx
                imghdr.field_of_view[1] = rFOVy
                imghdr.field_of_view[2] = rFOVz/rNz
                imghdr.position = ref_acq.position
                imghdr.read_dir = ref_acq.read_dir
                imghdr.phase_dir = ref_acq.phase_dir
                imghdr.slice_dir = ref_acq.slice_dir
                imghdr.patient_table_position = ref_acq.patient_table_position
                imghdr.average = ref_acq.idx.average
                imghdr.slice = ref_acq.idx.slice
                imghdr.contrast = contrast
                imghdr.phase = ref_acq.idx.phase
                imghdr.repetition = ref_acq.idx.repetition
                imghdr.set = ref_acq.idx.set
                imghdr.acquisition_time_stamp = ref_acq.acquisition_time_stamp
                imghdr.physiology_time_stamp = ref_acq.physiology_time_stamp
                imghdr.image_index = image_index
                image_index += 1

                mrd_image = Image(head=imghdr, data=combined)
                yield mrd_image

    for acq in input:
        if acq.idx.repetition != current_rep:
            # If we have a current buffer pass it on
            if buffer is not None and reference_acquisition is not None:
                yield from produce_image(buffer, reference_acquisition)

            # Reset buffer
            if acq.data.shape[-1] == eNx:
                readout_length = eNx
            else:
                readout_length = rNx  # Readout oversampling has been removed upstream

            buffer = np.zeros((ncontrasts, nslices, ncoils, eNz, eNy, readout_length), dtype=np.complex64)
            current_rep = acq.idx.repetition
            reference_acquisition = acq

        # Stuff into the buffer
        if buffer is not None:
            contrast = acq.idx.contrast if acq.idx.contrast is not None else 0
            slice = acq.idx.slice if acq.idx.slice is not None else 0
            k1 = acq.idx.kspace_encode_step_1 if acq.idx.kspace_encode_step_1 is not None else 0
            k2 = acq.idx.kspace_encode_step_2 if acq.idx.kspace_encode_step_2 is not None else 0
            buffer[contrast, slice, :, k2, k1 + ky_offset, :] = acq.data

    if buffer is not None and reference_acquisition is not None:
        yield from produce_image(buffer, reference_acquisition)
        buffer = None
        reference_acquisition = None

def reconstruct_ismrmrd_stream(input: BinaryIO, output: BinaryIO):
    with ProtocolDeserializer(input) as reader, ProtocolSerializer(output) as writer:
        stream = reader.deserialize()
        head = next(stream, None)
        if head is None:
            raise Exception("Could not read ISMRMRD header")
        if not isinstance(head, ismrmrdHeader):
            raise Exception("First item in stream is not an ISMRMRD header")
        writer.serialize(head)
        for item in stream_item_sink(
                accumulate_fft(head,
                    remove_oversampling(head,
                        acquisition_reader(stream)))):
            writer.serialize(item)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reconstructs an ISMRMRD stream")
    parser.add_argument('-i', '--input', type=str, required=False, help="Input stream, defaults to stdin")
    parser.add_argument('-o', '--output', type=str, required=False, help="Output stream, defaults to stdout")
    args = parser.parse_args()

    input = args.input if args.input is not None else sys.stdin.buffer
    output = args.output if args.output is not None else sys.stdout.buffer

    reconstruct_ismrmrd_stream(input, output)
