# -*- coding: utf-8 -*-

import ismrmrd
import ctypes
import numpy as np
import io

import nose.tools
from nose.tools import eq_

import test_common as common

def test_header():
    head = ismrmrd.ImageHeader()
    assert ctypes.sizeof(head) == 198


def test_new_instance():
    img = ismrmrd.Image()
    eq_(type(img.getHead()), ismrmrd.ImageHeader)
    eq_(img.getHead().data_type, ismrmrd.DATATYPE_CXFLOAT)
    eq_(type(img.data), np.ndarray)
    eq_(img.data.dtype, np.complex64)

    attr = "this is a fake attribute string"
    head = ismrmrd.ImageHeader()
    head.attribute_string_len = len(attr)       # must set attribute_string_len
    head.data_type = ismrmrd.DATATYPE_CXFLOAT   # must set data_type
    img = ismrmrd.Image(head, attribute_string=attr)
    eq_(img.attribute_string, attr)


def test_read_only_fields():
    img = ismrmrd.Image()
    for field in ['data_type', 'matrix_size', 'channels', 'attribute_string_len']:
        try:
            setattr(img, field, None)
        except AttributeError:
            pass
        else:
            raise Exception("Setting read-only attribute did not raise exception.")


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

    eq_(img.data.shape, (nchan, nz, ny, nx))
    eq_(img.data_type, ismrmrd.DATATYPE_CXDOUBLE)
    eq_(img.data.dtype, np.complex128)


def test_resize():
    pass

@nose.tools.with_setup(setup=common.seed_random_generators)
def test_initialization_sets_nonzero_version():

    image = ismrmrd.Image.from_array(common.create_random_array((128, 128), dtype=np.float32))

    assert image.version is not 0, \
        "Default image version should not be zero."


@nose.tools.with_setup(setup=common.seed_random_generators)
def test_initialization_with_array():

    image_data = common.create_random_array((256, 128), dtype=np.float32)
    image = ismrmrd.Image.from_array(image_data)

    assert np.array_equal(image_data.transpose(), image.data.squeeze()), \
        "Image data does not match data used to initialize image."


@nose.tools.with_setup(setup=common.seed_random_generators)
def test_initialization_with_array_and_acquisition():

    acquisition = common.create_random_acquisition()

    image_data = common.create_random_array((256, 128), dtype=np.float32)
    image = ismrmrd.Image.from_array(image_data, acquisition=acquisition)

    assert np.array_equal(image_data.transpose(), image.data.squeeze()), \
        "Image data does not match data used to initialize image."

    for field in ['version',
                  'measurement_uid',
                  'position',
                  'read_dir',
                  'phase_dir',
                  'slice_dir',
                  'patient_table_position',
                  'acquisition_time_stamp',
                  'physiology_time_stamp']:

        assert bytes(getattr(acquisition, field)) == bytes(getattr(image, field)), \
            "Acquisition header field not copied to image."


@nose.tools.with_setup(setup=common.seed_random_generators)
def test_initialization_with_array_and_header_properties():

    properties = common.create_random_image_properties()
    image_data = common.create_random_array((256, 512), dtype=np.float32)

    image = ismrmrd.Image.from_array(image_data, **properties)

    for field in properties:
        try:
            assert all(map(lambda a, b: a == b,
                           properties.get(field),
                           getattr(image, field))), \
                "Image property doesn't match initialization value: " + field
        except TypeError:
            assert properties.get(field) == getattr(image, field), \
                "Image property doesn't match initialization value: " + field


@nose.tools.with_setup(setup=common.seed_random_generators)
def test_initialization_with_2d_image():

    image_data = common.create_random_array((128, 64), dtype=np.float32)
    image = ismrmrd.Image.from_array(image_data)

    assert np.array_equal(image_data.transpose(), image.data.squeeze()), \
        "Image data does not match data used to initialize image."

    assert image.channels is 1, \
        "Unexpected number of channels: {}".format(image.channels)

    assert image.matrix_size == (1, 64, 128), \
        "Unexpected matrix size: {}".format(image.matrix_size)


@nose.tools.with_setup(setup=common.seed_random_generators)
def test_initialization_with_3d_image():

    image_data = common.create_random_array((128, 64, 32), dtype=np.float32)
    image = ismrmrd.Image.from_array(image_data)

    assert np.array_equal(image_data.transpose(), image.data.squeeze()), \
        "Image data does not match data used to initialize image."

    assert image.channels is 1, \
        "Unexpected number of channels: {}".format(image.channels)

    assert image.matrix_size == (32, 64, 128), \
        "Unexpected matrix size: {}".format(image.matrix_size)


@nose.tools.with_setup(setup=common.seed_random_generators)
def test_initialization_with_3d_image_and_channels():

    image_data = common.create_random_array((128, 64, 32, 16), dtype=np.float32)
    image = ismrmrd.Image.from_array(image_data)

    assert np.array_equal(image_data.transpose(), image.data.squeeze()), \
        "Image data does not match data used to initialize image."

    assert image.channels is 16, \
        "Unexpected number of channels: {}".format(image.channels)

    assert image.matrix_size == (32, 64, 128), \
        "Unexpected matrix size: {}".format(image.matrix_size)


@nose.tools.with_setup(setup=common.seed_random_generators)
def test_serialize_and_deserialize():

    image_data = common.create_random_array((128, 128), dtype=np.float32)
    image = ismrmrd.Image.from_array(image_data)

    with io.BytesIO(b'') as stream:
        image.serialize_into(stream.write)

        stream.seek(0)

        read_image = ismrmrd.Image.deserialize_from(stream.read)

        common.compare_images(image, read_image)


@nose.tools.with_setup(setup=common.seed_random_generators)
def test_to_and_from_bytes():

    image_data = common.create_random_array((128, 128), dtype=np.float32)
    image = ismrmrd.Image.from_array(image_data)

    read_image = ismrmrd.Image.from_bytes(image.to_bytes())

    common.compare_images(image, read_image)


@nose.tools.with_setup(setup=common.seed_random_generators)
def test_serialization_with_header_fields():

    image_data = common.create_random_array((128, 128), dtype=np.float32)
    image = ismrmrd.Image.from_array(image_data, **common.create_random_image_properties())

    read_image = ismrmrd.Image.from_bytes(image.to_bytes())

    common.compare_images(image, read_image)


@nose.tools.raises(ValueError)
@nose.tools.with_setup(setup=common.seed_random_generators)
def test_serialization_from_too_few_bytes():
    ismrmrd.Image.from_bytes(b'')


@nose.tools.with_setup(setup=common.seed_random_generators)
def test_serialization_of_unicode_attribute_string():

    image_data = common.create_random_array((128, 128), dtype=np.float32)
    image = ismrmrd.Image.from_array(image_data)

    image.attribute_string = u"يتم ترجمتها باستخدام مترجم جوجل."

    read_image = ismrmrd.Image.from_bytes(image.to_bytes())

    common.compare_images(image, read_image)
