
import ismrmrd

import numpy as np
import numpy.random

import random


def random_32bit_float():
    return numpy.random.rand(1).astype(np.float32)


def seed_random_generators(seed=42):
    numpy.random.seed(seed)
    random.seed(seed)


def random_tuple(size, random_fn):
    return tuple([random_fn() for _ in range(0, size)])


def create_random_acquisition_properties():
    return {
        'flags': random.randint(0, 1 << 64),
        'measurement_uid': random.randint(0, 1 << 32),
        'scan_counter': random.randint(0, 1 << 32),
        'acquisition_time_stamp': random.randint(0, 1 << 32),
        'physiology_time_stamp': random_tuple(3, lambda: random.randint(0, 1 << 32)),
        'available_channels': random.randint(0, 1 << 16),
        'channel_mask': random_tuple(16, lambda: random.randint(0, 1 << 64)),
        'discard_pre': random.randint(0, 1 << 16),
        'discard_post': random.randint(0, 1 << 16),
        'center_sample': random.randint(0, 1 << 16),
        'encoding_space_ref': random.randint(0, 1 << 16),
        'sample_time_us': random_32bit_float(),
        'position': random_tuple(3, random_32bit_float),
        'read_dir': random_tuple(3, random_32bit_float),
        'phase_dir': random_tuple(3, random_32bit_float),
        'slice_dir': random_tuple(3, random_32bit_float),
        'patient_table_position': random_tuple(3, random_32bit_float),
        'idx': ismrmrd.EncodingCounters(),
        'user_int': random_tuple(8, lambda: random.randint(0, 1 << 31)),
        'user_float': random_tuple(8, random_32bit_float)
    }


def create_random_image_properties():
    return {
        'flags': random.randint(0, 1 << 64),
        'measurement_uid': random.randint(0, 1 << 32),
        'field_of_view': random_tuple(3, random_32bit_float),
        'position': random_tuple(3, random_32bit_float),
        'read_dir': random_tuple(3, random_32bit_float),
        'phase_dir': random_tuple(3, random_32bit_float),
        'slice_dir': random_tuple(3, random_32bit_float),
        'patient_table_position': random_tuple(3, random_32bit_float),
        'average': random.randint(0, 1 << 16),
        'slice': random.randint(0, 1 << 16),
        'contrast': random.randint(0, 1 << 16),
        'phase': random.randint(0, 1 << 16),
        'repetition': random.randint(0, 1 << 16),
        'set': random.randint(0, 1 << 16),
        'acquisition_time_stamp': random.randint(0, 1 << 32),
        'physiology_time_stamp': random_tuple(3, lambda: random.randint(0, 1 << 32)),
        'image_index': random.randint(0, 1 << 16),
        'image_series_index': random.randint(0, 1 << 16),
        'user_int': random_tuple(8, lambda: random.randint(0, 1 << 31)),
        'user_float': random_tuple(8, random_32bit_float),
    }


def create_random_waveform_properties():
    return {
        'flags': random.randint(0, 1 << 64),
        'measurement_uid': random.randint(0, 1 << 32),
        'waveform_id': random.randint(0, 1 << 16),
        'scan_counter': random.randint(0, 1 << 32),
        'time_stamp': random.randint(0, 1 << 32),
        'sample_time_us': random_32bit_float()
    }


def create_random_array(shape, dtype):
    array = numpy.random.random_sample(shape)
    return array.astype(dtype)


def create_random_data(shape=(32, 256)):
    array = numpy.random.random_sample(shape) + 1j * numpy.random.random_sample(shape)
    return array.astype(np.complex64)


def create_random_trajectory(shape=(256, 2)):
    return create_random_array(shape, dtype=np.float32)


def create_random_waveform_data(shape=(32, 256)):
    data = numpy.random.randint(0, 1 << 32, size=shape)
    return data.astype(np.uint32)


def create_random_acquisition(seed=42):

    random.seed(seed)
    numpy.random.seed(seed)

    data = create_random_data((32, 256))
    traj = create_random_trajectory((256, 2))
    header = create_random_acquisition_properties()

    return ismrmrd.Acquisition.from_array(data, traj, **header)


def create_random_image(seed=42):

    random.seed(seed)
    numpy.random.seed(seed)

    data = create_random_array((256, 256), dtype=np.float32)
    header = create_random_image_properties()

    image = ismrmrd.Image.from_array(data, **header)
    image.attribute_string = "This is a random attribute: {}".format(random.randint(0, 1000))

    return image


def create_random_waveform(seed=42):

    random.seed(seed)
    numpy.random.seed(seed)

    data = numpy.random.randint(0, 1 << 16, size=(4, 256))
    data = data.astype(np.uint32)
    header = create_random_waveform_properties()

    return ismrmrd.Waveform.from_array(data, **header)


def compare_acquisitions(acquisition, *acquisitions):

    for other in acquisitions:

        assert np.array_equal(acquisition.data, other.data), \
            "Acquisition data does not match."

        assert np.array_equal(acquisition.traj, other.traj), \
            "Acquisition trajectory does not match."

        assert bytes(acquisition.getHead()) == bytes(other.getHead()), \
            "Acquisition header does not match."


def compare_images(image, *images):

    for other in images:

        assert np.array_equal(image.data, other.data), \
            "Image data does not match."

        assert bytes(image.getHead()) == bytes(other.getHead()), \
            "Image header does not match."

        assert image.attribute_string == other.attribute_string, \
            "Image attribute string does not match."


def compare_waveforms(waveform, *waveforms):

    for other in waveforms:

        assert bytes(waveform.getHead()) == bytes(other.getHead()), \
            "Waveform header does not match."

        assert np.array_equal(waveform.data, other.data), \
            "Waveform data does not match."
