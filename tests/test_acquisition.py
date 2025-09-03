import ismrmrd
import ctypes
import numpy as np
import io
import pytest

import test_common as common


def test_encoding_counters():
    idx = ismrmrd.EncodingCounters()
    assert ctypes.sizeof(idx) == 34


def test_header():
    head = ismrmrd.AcquisitionHeader()
    assert ctypes.sizeof(head) == 340


def test_new_instance():
    acq = ismrmrd.Acquisition()
    assert type(acq.getHead()) == ismrmrd.AcquisitionHeader
    assert type(acq.data) == np.ndarray
    assert acq.data.dtype == np.complex64
    assert type(acq.traj) == np.ndarray
    assert acq.traj.dtype == np.float32


def test_read_only_fields():
    acq = ismrmrd.Acquisition()

    for field in ['number_of_samples', 'active_channels', 'trajectory_dimensions']:
        with pytest.raises(AttributeError):
            setattr(acq, field, None)


def test_resize():
    acq = ismrmrd.Acquisition()
    nsamples, nchannels, ntrajdims = 128, 8, 3
    acq.resize(nsamples, nchannels, ntrajdims)
    assert acq.data.shape == (nchannels, nsamples)
    assert acq.traj.shape == (nsamples, ntrajdims)
    head = acq.getHead()
    assert head.number_of_samples == nsamples
    assert head.active_channels == nchannels
    assert head.trajectory_dimensions == ntrajdims


def test_set_head():
    acq = ismrmrd.Acquisition()
    head = ismrmrd.AcquisitionHeader()
    nsamples, nchannels, ntrajdims = 128, 8, 3
    head.number_of_samples = nsamples
    head.active_channels = nchannels
    head.trajectory_dimensions = ntrajdims

    acq.setHead(head)

    assert acq.data.shape == (nchannels, nsamples)
    assert acq.traj.shape == (nsamples, ntrajdims)


def test_flags():
    acq = ismrmrd.Acquisition()

    for i in range(1, 65):
        assert not acq.is_flag_set(i)

    for i in range(1, 65):
        acq.set_flag(i)
        assert acq.is_flag_set(i)

    for i in range(1, 65):
        acq.clear_flag(i)
        assert not acq.is_flag_set(i)

    assert acq.flags == 0

    for i in range(1, 65):
        acq.set_flag(i)

    acq.clear_all_flags()

    for i in range(1, 65):
        assert not acq.is_flag_set(i)


def test_clearing_unset_flag_does_not_set_other_flags():
    acquisition = ismrmrd.Acquisition()

    assert acquisition.flags == 0, \
        "Fresh acquisitions should not have any flags set."

    acquisition.clearFlag(ismrmrd.ACQ_FIRST_IN_ENCODE_STEP1)

    assert acquisition.flags == 0, \
        "Clearing an unset flag sets other flags."


def test_acquisition_equality_test_header_field():
    a = common.create_random_acquisition(42)
    b = common.create_random_acquisition(42)

    assert a == b

    a.flags -= 1

    assert a != b


def test_acquisition_equality_test_header_array():
    a = common.create_random_acquisition(42)
    b = common.create_random_acquisition(42)

    assert a == b

    a.position[1] += a.position[1] * 0.5

    assert a != b


def test_initialization_from_array():
    nchannels = 32
    nsamples = 256

    data = common.create_random_data((nchannels, nsamples))
    acquisition = ismrmrd.Acquisition.from_array(data)

    assert np.array_equal(acquisition.data, data)


def test_initialization_from_arrays():
    nchannels = 32
    nsamples = 256
    trajectory_dimensions = 2

    data = common.create_random_data((nchannels, nsamples))
    trajectory = common.create_random_trajectory((nsamples, trajectory_dimensions))

    acquisition = ismrmrd.Acquisition.from_array(data, trajectory)

    assert np.array_equal(acquisition.data, data)
    assert np.array_equal(acquisition.traj, trajectory)


def test_initialization_sets_nonzero_version():
    acquisition = ismrmrd.Acquisition.from_array(common.create_random_data())

    assert acquisition.version != 0, \
        "Default acquisition version should not be zero."


def test_initialization_with_header_fields():
    fields = {
        'version': 2,
        'measurement_uid':  123456789,
        'available_channels': 64,
    }

    data = common.create_random_data()
    acquisition = ismrmrd.Acquisition.from_array(data, **fields)

    for field in fields:

        assert fields.get(field) == getattr(acquisition, field), \
            "Field {} not preserved by acquisition. ({} != {})".format(field, fields.get(field),
                                                                       getattr(acquisition, field))


def test_initialization_with_illegal_header_value():
    with pytest.raises(TypeError):
        ismrmrd.Acquisition.from_array(common.create_random_data(), version='Bad version')


def test_serialize_and_deserialize():
    acquisition = ismrmrd.Acquisition.from_array(common.create_random_data())

    with io.BytesIO() as stream:
        acquisition.serialize_into(stream.write)

        # Rewind the stream, so we can read the bytes back.
        stream.seek(0)

        deserialized_acquisition = ismrmrd.Acquisition.deserialize_from(stream.read)

        assert acquisition == deserialized_acquisition


def test_to_and_from_bytes():
    acquisition = ismrmrd.Acquisition.from_array(common.create_random_data())

    deserialized_acquisition = ismrmrd.Acquisition.from_bytes(acquisition.to_bytes())

    assert acquisition == deserialized_acquisition


def test_serialization_with_header_fields():
    properties = common.create_random_acquisition_properties()
    data = common.create_random_data()
    trajectory = common.create_random_trajectory()

    acquisition = ismrmrd.Acquisition.from_array(data, trajectory, **properties)
    deserialized_acquisition = ismrmrd.Acquisition.from_bytes(acquisition.to_bytes())

    assert acquisition == deserialized_acquisition


def test_deserialization_from_too_few_bytes():
    with pytest.raises(ValueError):
        ismrmrd.Acquisition.from_bytes(b'')
