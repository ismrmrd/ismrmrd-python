# -*- coding: utf-8 -*-

import ismrmrd
import ctypes
import numpy as np
import io
import pytest

import test_common as common

def test_header():
    head = ismrmrd.ImageHeader()
    assert ctypes.sizeof(head) == 198


def test_new_instance():
    img = ismrmrd.Image()
    assert type(img.getHead()) == ismrmrd.ImageHeader
    assert img.getHead().data_type == ismrmrd.DATATYPE_CXFLOAT
    assert type(img.data) == np.ndarray
    assert img.data.dtype == np.complex64

    attr = "<?xml version='1.0' encoding='UTF-8'?>\n<ismrmrdMeta><meta><name>rando</name><value>blah</value></meta></ismrmrdMeta>"

    head = ismrmrd.ImageHeader()
    head.attribute_string_len = len(attr)       # must set attribute_string_len
    head.data_type = ismrmrd.DATATYPE_CXFLOAT   # must set data_type
    img = ismrmrd.Image(head, attribute_string=attr)
    assert img.attribute_string == attr

def test_read_only_fields():
    img = ismrmrd.Image()
    for field in ['data_type', 'matrix_size', 'channels', 'attribute_string_len']:
        with pytest.raises(AttributeError):
            setattr(img, field, None)


def test_set_head():
    img = ismrmrd.Image()
    nchan, nx, ny, nz = 8, 256, 128, 32
    head = ismrmrd.ImageHeader()
    head.data_type = ismrmrd.DATATYPE_CXDOUBLE
    head.channels = nchan
    head.matrix_size[0] = nx
    head.matrix_size[1] = ny
    head.matrix_size[2] = nz

    img.setHead(head)

    assert img.data.shape == (nchan, nz, ny, nx)
    assert img.data_type == ismrmrd.DATATYPE_CXDOUBLE
    assert img.data.dtype == np.complex128


def test_resize():
    pass

def test_initialization_sets_nonzero_version():
    image = ismrmrd.Image.from_array(common.create_random_array((128, 128), dtype=np.float32))
    assert image.version != 0

def test_initialization_with_array():
    image_data = common.create_random_array((256, 128), dtype=np.float32)
    image = ismrmrd.Image.from_array(image_data)
    assert np.array_equal(image_data.transpose(), image.data.squeeze())

def test_initialization_with_array_and_acquisition():
    acquisition = common.create_random_acquisition()
    image_data = common.create_random_array((256, 128), dtype=np.float32)
    image = ismrmrd.Image.from_array(image_data, acquisition=acquisition)
    assert np.array_equal(image_data.transpose(), image.data.squeeze())
    for field in ['version', 'measurement_uid', 'position', 'read_dir', 'phase_dir', 'slice_dir', 'patient_table_position', 'acquisition_time_stamp', 'physiology_time_stamp']:
        assert bytes(getattr(acquisition, field)) == bytes(getattr(image, field))

def test_initialization_with_array_and_header_properties():
    properties = common.create_random_image_properties()
    image_data = common.create_random_array((256, 512), dtype=np.float32)
    image = ismrmrd.Image.from_array(image_data, **properties)
    for field in properties:
        expected = properties.get(field)
        actual = getattr(image, field)
        # If both are sequences and contain floats, use np.allclose
        if isinstance(expected, (tuple, list)) and hasattr(actual, '__len__') and len(expected) == len(actual):
            try:
                expected_arr = np.array(expected, dtype=float)
                actual_arr = np.array(actual, dtype=float)
                assert np.allclose(expected_arr, actual_arr), f"Field '{field}' does not match: {expected_arr} != {actual_arr}"
            except Exception:
                for i, (a, b) in enumerate(zip(expected, actual)):
                    assert a == b, f"Field '{field}' index {i} does not match: {a} != {b}"
        else:
            assert expected == actual, f"Field '{field}' does not match: {expected} != {actual}"

def test_initialization_with_2d_image():
    image_data = common.create_random_array((128, 64), dtype=np.float32)
    image = ismrmrd.Image.from_array(image_data)
    assert np.array_equal(image_data.transpose(), image.data.squeeze())
    assert image.channels == 1
    assert image.matrix_size == (1, 64, 128)

def test_initialization_with_3d_image():
    image_data = common.create_random_array((128, 64, 32), dtype=np.float32)
    image = ismrmrd.Image.from_array(image_data)
    assert np.array_equal(image_data.transpose(), image.data.squeeze())
    assert image.channels == 1
    assert image.matrix_size == (32, 64, 128)

def test_initialization_with_3d_image_and_channels():
    image_data = common.create_random_array((128, 64, 32, 16), dtype=np.float32)
    image = ismrmrd.Image.from_array(image_data)
    assert np.array_equal(image_data.transpose(), image.data.squeeze())
    assert image.channels == 16
    assert image.matrix_size == (32, 64, 128)

def test_serialize_and_deserialize():
    image_data = common.create_random_array((128, 128), dtype=np.float32)
    image = ismrmrd.Image.from_array(image_data)
    with io.BytesIO(b'') as stream:
        image.serialize_into(stream.write)
        stream.seek(0)
        read_image = ismrmrd.Image.deserialize_from(stream.read)
        assert image == read_image

def test_to_and_from_bytes():
    image_data = common.create_random_array((128, 128), dtype=np.float32)
    image = ismrmrd.Image.from_array(image_data)
    read_image = ismrmrd.Image.from_bytes(image.to_bytes())
    assert image == read_image

def test_serialization_with_header_fields():
    image_data = common.create_random_array((128, 128), dtype=np.float32)
    image = ismrmrd.Image.from_array(image_data, **common.create_random_image_properties())
    read_image = ismrmrd.Image.from_bytes(image.to_bytes())
    assert image == read_image

def test_serialization_from_too_few_bytes():
    with pytest.raises(ValueError):
        ismrmrd.Image.from_bytes(b'')
