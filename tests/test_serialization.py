from ctypes import c_float, c_int32, c_uint, c_uint16, c_uint32, c_uint64
import io
import numpy as np
import test_common as common
from ismrmrd.acquisition import Acquisition, EncodingCounters, AcquisitionHeader
from ismrmrd.image import Image, ImageHeader
from ismrmrd.meta import Meta
from ismrmrd.waveform import Waveform, WaveformHeader
from ismrmrd.serialization import ProtocolSerializer, ProtocolDeserializer
from ismrmrd.xsd import ismrmrdHeader, CreateFromDocument
from test_file import example_header

def make_acquisition():
    # Build header
    header = AcquisitionHeader()
    header.version = 1
    header.flags = 2
    header.measurement_uid = 123
    header.scan_counter = 1
    header.acquisition_time_stamp = 456
    header.physiology_time_stamp[:] = [1, 2, 3]
    header.number_of_samples = 4
    header.available_channels = 2
    header.active_channels = 2
    header.channel_mask[:] = [1] * 16
    header.discard_pre = 0
    header.discard_post = 0
    header.center_sample = 2
    header.encoding_space_ref = 0
    header.trajectory_dimensions = 2
    header.sample_time_us = 1.0
    header.position[:] = [0.0, 0.0, 0.0]
    header.read_dir[:] = [1.0, 0.0, 0.0]
    header.phase_dir[:] = [0.0, 1.0, 0.0]
    header.slice_dir[:] = [0.0, 0.0, 1.0]
    header.patient_table_position[:] = [0.0, 0.0, 0.0]
    header.idx = EncodingCounters()
    header.idx.kspace_encode_step_1 = 0
    header.idx.kspace_encode_step_2 = 0
    header.idx.average = 0
    header.idx.slice = 0
    header.idx.contrast = 0
    header.idx.phase = 0
    header.idx.repetition = 0
    header.idx.set = 0
    header.idx.segment = 0
    header.idx.user[:] = [0] * 8
    header.user_int[:] = [0] * 8
    header.user_float[:] = [0.0] * 8
    # Build data arrays
    trajectory = np.ones((header.number_of_samples, header.trajectory_dimensions), dtype='float32')
    data = np.ones((header.active_channels, header.number_of_samples), dtype='complex64')
    # Construct Acquisition
    acq = Acquisition(header, data, trajectory)
    return acq

def make_image():
    # Build header
    header = ImageHeader()
    header.version = 1
    header.data_type = 5  # FLOAT
    header.flags = 2
    header.measurement_uid = 123
    header.matrix_size[:] = [2, 2, 2]
    header.field_of_view[:] = [1.0, 1.0, 1.0]
    header.channels = 1
    header.position[:] = [0.0, 0.0, 0.0]
    header.read_dir[:] = [1.0, 0.0, 0.0]
    header.phase_dir[:] = [0.0, 1.0, 0.0]
    header.slice_dir[:] = [0.0, 0.0, 1.0]
    header.patient_table_position[:] = [0.0, 0.0, 0.0]
    header.average = 0
    header.slice = 0
    header.contrast = 0
    header.phase = 0
    header.repetition = 0
    header.set = 0
    header.acquisition_time_stamp = 456
    header.physiology_time_stamp[:] = [1, 2, 3]
    header.image_type = 1
    header.image_index = 1
    header.image_series_index = 1
    header.user_int[:] = [0] * 8
    header.user_float[:] = [0.0] * 8

    data = np.ones((1, 2, 2, 2), dtype='float32')
    meta = Meta({"foo": "bar"})
    img = Image(head=header, data=data, meta=meta)
    return img

def make_waveform():
    head = WaveformHeader()
    head.version = 1
    head.flags = 2
    head.measurement_uid = 123
    head.scan_counter = 1
    head.time_stamp = 456
    head.number_of_samples = 4

    head.channels = 2
    head.sample_time_us = 1.0
    head.waveform_id = 42

    data = np.ones((2, 4), dtype=np.uint32)
    wf = Waveform(head, data)
    return wf

def test_acquisition_serialization():
    acq = common.create_random_acquisition()
    stream = io.BytesIO()
    serializer = ProtocolSerializer(stream)
    serializer.serialize(acq)
    serializer.close()
    stream.seek(0)
    deserializer = ProtocolDeserializer(stream)
    objects = list(deserializer.deserialize())
    assert len(objects) == 1
    acq2 = objects[0]
    assert np.allclose(acq.data, acq2.data)
    assert np.allclose(acq.traj, acq2.traj)
    assert acq.number_of_samples == acq2.number_of_samples
    assert acq.active_channels == acq2.active_channels
    assert acq.flags == acq2.flags
    assert acq.idx == acq2.idx

def test_image_serialization():
    img = common.create_random_image()
    stream = io.BytesIO()
    serializer = ProtocolSerializer(stream)
    serializer.serialize(img)
    serializer.close()
    stream.seek(0)
    deserializer = ProtocolDeserializer(stream)
    objects = list(deserializer.deserialize())
    assert len(objects) == 1
    img2 = objects[0]
    assert np.allclose(img.data, img2.data)
    assert img.matrix_size == img2.matrix_size
    assert img.channels == img2.channels
    assert img.meta == img2.meta
    assert img.attribute_string == img2.attribute_string

def test_waveform_serialization():
    wf = common.create_random_waveform()
    stream = io.BytesIO()
    serializer = ProtocolSerializer(stream)
    serializer.serialize(wf)
    serializer.close()
    stream.seek(0)
    deserializer = ProtocolDeserializer(stream)
    objects = list(deserializer.deserialize())
    assert len(objects) == 1
    wf2 = objects[0]
    assert np.allclose(wf.data, wf2.data)
    assert wf.number_of_samples == wf2.number_of_samples
    assert wf.channels == wf2.channels
    assert wf.waveform_id == wf2.waveform_id


def test_ismrmrd_header_serialization():
    header = common.create_example_ismrmrd_header()
    stream = io.BytesIO()
    serializer = ProtocolSerializer(stream)
    serializer.serialize(header)
    serializer.close()
    stream.seek(0)
    deserializer = ProtocolDeserializer(stream)
    objects = list(deserializer.deserialize())
    assert len(objects) == 1
    header2 = objects[0]
    # Compare by converting both to XML strings
    assert header.toXML() == header2.toXML()


def test_ndarray_serialization():
    arr = common.create_random_ndarray()
    stream = io.BytesIO()
    serializer = ProtocolSerializer(stream)
    serializer.serialize(arr)
    serializer.close()
    stream.seek(0)
    deserializer = ProtocolDeserializer(stream)
    objects = list(deserializer.deserialize())
    assert len(objects) == 1
    arr2 = objects[0]
    assert np.array_equal(arr, arr2)
    assert arr.dtype == arr2.dtype
    assert arr.shape == arr2.shape


def test_text_serialization():
    text = "Hello, ISMRMRD! This is a test text message with special characters: àáâãäåæçèéêë 123456789 !@#$%^&*()"
    stream = io.BytesIO()
    serializer = ProtocolSerializer(stream)
    serializer.serialize(text)
    serializer.close()
    stream.seek(0)
    deserializer = ProtocolDeserializer(stream)
    objects = list(deserializer.deserialize())
    assert len(objects) == 1
    text2 = objects[0]
    assert text == text2
    assert isinstance(text2, str)


def test_interleaved_serialization():
    """Test serialization and deserialization of multiple interleaved objects."""
    # Create test objects
    acq = common.create_random_acquisition()
    img = common.create_random_image()
    wf = common.create_random_waveform()
    header = common.create_example_ismrmrd_header()
    arr = common.create_random_ndarray()
    text = "Test interleaved text message 🚀"

    # Serialize all objects in a specific order
    stream = io.BytesIO()
    serializer = ProtocolSerializer(stream)
    serializer.serialize(acq)
    serializer.serialize(text)
    serializer.serialize(img)
    serializer.serialize(header)
    serializer.serialize(arr)
    serializer.serialize(wf)
    serializer.close()

    # Deserialize and verify order and content
    stream.seek(0)
    deserializer = ProtocolDeserializer(stream)
    objects = list(deserializer.deserialize())
    assert len(objects) == 6

    # First object: Acquisition
    obj1 = objects[0]
    assert isinstance(obj1, Acquisition)
    assert np.allclose(acq.data, obj1.data)
    assert np.allclose(acq.traj, obj1.traj)
    assert acq.flags == obj1.flags

    # Second object: Text
    obj2 = objects[1]
    assert isinstance(obj2, str)
    assert text == obj2

    # Third object: Image
    obj3 = objects[2]
    assert isinstance(obj3, Image)
    assert np.allclose(img.data, obj3.data)
    assert img.matrix_size == obj3.matrix_size
    assert img.channels == obj3.channels

    # Fourth object: Header
    obj4 = objects[3]
    assert isinstance(obj4, type(header))  # ismrmrdHeader type
    assert header.toXML() == obj4.toXML()

    # Fifth object: NDArray
    obj5 = objects[4]
    assert isinstance(obj5, np.ndarray)
    assert np.array_equal(arr, obj5)
    assert arr.dtype == obj5.dtype
    assert arr.shape == obj5.shape

    # Sixth object: Waveform
    obj6 = objects[5]
    assert isinstance(obj6, Waveform)
    assert np.allclose(wf.data, obj6.data)
    assert wf.number_of_samples == obj6.number_of_samples
    assert wf.channels == obj6.channels