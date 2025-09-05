import ismrmrd
import ctypes
import numpy as np
import numpy.random
import io
import pytest

import test_common as common


def test_initialization_from_array():
    nchannels = 32
    nsamples = 256

    data = numpy.random.randint(0, 1 << 32, size=(nchannels, nsamples),dtype=np.uint32)

    waveform = ismrmrd.Waveform.from_array(data)

    assert np.array_equal(waveform.data, data), \
        "Waveform data does not match data used to initialize waveform."


def test_initialization_sets_nonzero_version():
    waveform = common.create_random_waveform()

    assert waveform.version != 0, \
        "Default acquisition version should not be zero."


def test_initialization_with_header_fields():
    fields = common.create_random_waveform_properties()

    waveform = ismrmrd.Waveform.from_array(common.create_random_waveform_data(), **fields)

    for field in fields:

        expected = fields.get(field)
        actual = getattr(waveform, field)
        # Use np.isclose for scalar float comparison
        if isinstance(expected, float) or isinstance(actual, float):
            assert np.isclose(float(expected), float(actual)), f"Field '{field}' does not match: {expected} != {actual}"
        elif isinstance(expected, (tuple, list)) and hasattr(actual, '__len__') and len(expected) == len(actual):
            for i, (a, b) in enumerate(zip(expected, actual)):
                assert a == b, f"Field '{field}' index {i} does not match: {a} != {b}"
        else:
            assert expected == actual, f"Field '{field}' does not match: {expected} != {actual}"


def test_initialization_with_illegal_header_value():
    with pytest.raises(TypeError):
        ismrmrd.Waveform.from_array(common.create_random_waveform_data(), version='Bad version')


def test_serialize_and_deserialize():
    waveform = common.create_random_waveform()

    with io.BytesIO() as stream:
        waveform.serialize_into(stream.write)

        # Rewind the stream, so we can read the bytes back.
        stream.seek(0)

        deserialized_waveform = ismrmrd.Waveform.deserialize_from(stream.read)

        assert waveform == deserialized_waveform


def test_to_and_from_bytes():
    waveform = common.create_random_waveform()

    deserialized_waveform = ismrmrd.Waveform.from_bytes(waveform.to_bytes())

    assert waveform == deserialized_waveform


def test_serialization_with_header_fields():
    properties = common.create_random_waveform_properties()
    data = common.create_random_waveform_data()

    waveform = ismrmrd.Waveform.from_array(data, **properties)
    deserialized_waveform = ismrmrd.Waveform.from_bytes(waveform.to_bytes())

    assert waveform == deserialized_waveform


def test_deserialization_from_too_few_bytes():
    with pytest.raises(ValueError):
        ismrmrd.Acquisition.from_bytes(b'')


def test_waveformheader_size():
    wav = ismrmrd.WaveformHeader()
    assert ctypes.sizeof(wav) == 40

