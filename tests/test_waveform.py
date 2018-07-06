
import ismrmrd
import ctypes

import numpy as np
import numpy.random

import io

import nose.tools

import test_common as common

@nose.tools.with_setup(setup=common.seed_random_generators)
def test_initialization_from_array():

    nchannels = 32
    nsamples = 256

    data = numpy.random.randint(0, 1 << 32, size=(nchannels, nsamples))
    data = data.astype(np.uint32)

    waveform = ismrmrd.Waveform.from_array(data)

    assert np.array_equal(waveform.data, data), \
        "Waveform data does not match data used to initialize waveform."


@nose.tools.with_setup(setup=common.seed_random_generators)
def test_initialization_sets_nonzero_version():

    waveform = common.create_random_waveform()

    assert waveform.version is not 0, \
        "Default acquisition version should not be zero."


@nose.tools.with_setup(setup=common.seed_random_generators)
def test_initialization_with_header_fields():

    fields = common.create_random_waveform_properties()

    waveform = ismrmrd.Waveform.from_array(common.create_random_waveform_data(), **fields)

    for field in fields:

        assert fields.get(field) == getattr(waveform, field), \
            "Field {} not preserved by waveform. ({} != {})".format(field,
                                                                    fields.get(field),
                                                                    getattr(waveform, field))


@nose.tools.raises(TypeError)
def test_initialization_with_illegal_header_value():
    ismrmrd.Waveform.from_array(common.create_random_waveform_data(), version='Bad version')


@nose.tools.with_setup(setup=common.seed_random_generators)
def test_serialize_and_deserialize():

    waveform = common.create_random_waveform()

    with io.BytesIO() as stream:
        waveform.serialize_into(stream.write)

        # Rewind the stream, so we can read the bytes back.
        stream.seek(0)

        deserialized_waveform = ismrmrd.Waveform.deserialize_from(stream.read)

        common.compare_waveforms(waveform, deserialized_waveform)


@nose.tools.with_setup(setup=common.seed_random_generators)
def test_to_and_from_bytes():

    waveform = common.create_random_waveform()

    deserialized_waveform = ismrmrd.Waveform.from_bytes(waveform.to_bytes())

    common.compare_waveforms(waveform, deserialized_waveform)


@nose.tools.with_setup(setup=common.seed_random_generators)
def test_serialization_with_header_fields():

    properties = common.create_random_waveform_properties()
    data = common.create_random_waveform_data()

    waveform = ismrmrd.Waveform.from_array(data, **properties)
    deserialized_waveform = ismrmrd.Waveform.from_bytes(waveform.to_bytes())

    common.compare_waveforms(waveform, deserialized_waveform)


@nose.tools.raises(ValueError)
def test_deserialization_from_too_few_bytes():
    ismrmrd.Acquisition.from_bytes(b'')


def test_waveformheader_size():
    wav = ismrmrd.WaveformHeader()
    assert ctypes.sizeof(wav) == 40

