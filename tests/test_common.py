import ismrmrd

import numpy as np
import numpy.random

import random

import ismrmrd.xsd


example_header = """<?xml version="1.0" encoding="utf-8"?>
<ismrmrdHeader xmlns="http://www.ismrm.org/ISMRMRD" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.ismrm.org/ISMRMRD ismrmrd.xsd">
   <experimentalConditions>
      <H1resonanceFrequency_Hz>32130323</H1resonanceFrequency_Hz>
   </experimentalConditions>
   <encoding>
      <encodedSpace>
         <matrixSize>
            <x>64</x>
            <y>64</y>
            <z>1</z>
         </matrixSize>
         <fieldOfView_mm>
            <x>300</x>
            <y>300</y>
            <z>40</z>
         </fieldOfView_mm>
      </encodedSpace>
      <reconSpace>
         <matrixSize>
            <x>64</x>
            <y>64</y>
            <z>1</z>
         </matrixSize>
         <fieldOfView_mm>
            <x>300</x>
            <y>300</y>
            <z>40</z>
         </fieldOfView_mm>
      </reconSpace>
      <trajectory>radial</trajectory>
      <encodingLimits>
      </encodingLimits>
   </encoding>
</ismrmrdHeader>
"""


def create_example_ismrmrd_header():
    """Create a sample ISMRMRD header using the example from test_file.py."""
    return ismrmrd.xsd.CreateFromDocument(example_header)

def create_random_ndarray():
    """Create a sample multi-dimensional numpy array."""
    # Create a 4D array to test multiple dimensions: (batch, channels, height, width)
    return np.random.rand(2, 8, 64, 64).astype(np.float32)

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
        'sample_time_us': random.random(),
        'position': random_tuple(3, random.random),
        'read_dir': random_tuple(3, random.random),
        'phase_dir': random_tuple(3, random.random),
        'slice_dir': random_tuple(3, random.random),
        'patient_table_position': random_tuple(3, random.random),
        'idx': ismrmrd.EncodingCounters(),
        'user_int': random_tuple(8, lambda: random.randint(0, 1 << 31)),
        'user_float': random_tuple(8, random.random)
    }


def create_random_image_properties():
    return {
        'flags': random.randint(0, 1 << 64),
        'measurement_uid': random.randint(0, 1 << 32),
        'field_of_view': random_tuple(3, random.random),
        'position': random_tuple(3, random.random),
        'read_dir': random_tuple(3, random.random),
        'phase_dir': random_tuple(3, random.random),
        'slice_dir': random_tuple(3, random.random),
        'patient_table_position': random_tuple(3, random.random),
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
        'user_float': random_tuple(8, random.random),
    }


def create_random_waveform_properties():
    return {
        'flags': random.randint(0, 1 << 64),
        'measurement_uid': random.randint(0, 1 << 32),
        'waveform_id': random.randint(0, 1 << 16),
        'scan_counter': random.randint(0, 1 << 32),
        'time_stamp': random.randint(0, 1 << 32),
        'sample_time_us': random.random()
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
    return  numpy.random.randint(0, 1 << 32, size=shape,dtype=np.uint32)


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
    image.meta = {"Random attribute": str(random.randint(0,1000))}

    return image


def create_random_waveform(seed=42):

    random.seed(seed)
    numpy.random.seed(seed)

    data = numpy.random.randint(0, 1 << 16, size=(4, 256))
    data = data.astype(np.uint32)
    header = create_random_waveform_properties()

    return ismrmrd.Waveform.from_array(data, **header)


def compare_acquisitions(a, b):
    assert type(a) == type(b)
    assert a.data.shape == b.data.shape
    assert np.allclose(a.data, b.data)
    assert a.traj.shape == b.traj.shape
    assert np.allclose(a.traj, b.traj)
    for key in a.__dict__:
        if key not in ['data', 'traj']:
            aval = getattr(a, key)
            bval = getattr(b, key)
            if isinstance(aval, np.ndarray) and isinstance(bval, np.ndarray):
                assert np.array_equal(aval, bval), f"Field '{key}' does not match: {aval} != {bval}"
            else:
                assert aval == bval, f"Field '{key}' does not match: {aval} != {bval}"


def compare_images(a, b):
    assert type(a) == type(b)
    assert a.data.shape == b.data.shape
    assert np.allclose(a.data, b.data)
    for key in a.__dict__:
        if key != 'data':
            aval = getattr(a, key)
            bval = getattr(b, key)
            if isinstance(aval, np.ndarray) and isinstance(bval, np.ndarray):
                assert np.array_equal(aval, bval), f"Field '{key}' does not match: {aval} != {bval}"
            else:
                assert aval == bval, f"Field '{key}' does not match: {aval} != {bval}"


def compare_waveforms(a, b):
    assert type(a) == type(b)
    assert a.data.shape == b.data.shape
    assert np.array_equal(a.data, b.data)
    for key in a.__dict__:
        if key != 'data':
            aval = getattr(a, key)
            bval = getattr(b, key)
            if isinstance(aval, np.ndarray) and isinstance(bval, np.ndarray):
                assert np.array_equal(aval, bval), f"Field '{key}' does not match: {aval} != {bval}"
            else:
                assert aval == bval, f"Field '{key}' does not match: {aval} != {bval}"
