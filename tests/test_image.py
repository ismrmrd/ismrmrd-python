import ismrmrd
import ctypes
import numpy as np

from nose.tools import eq_

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
        except:
            pass
        else:
            assert False, "assigned to read-only field of Image"

def test_resize():
    img = ismrmrd.Image()
    nchan, nx, ny, nz = 8, 256, 128, 32
    img.resize(nchan, nz, ny, nx)
    eq_(img.data.shape, (nchan, nz, ny, nx))
    eq_(img.matrix_size, (nz, ny, nx))
    # TODO: address the following:
    # head = img.getHead()
    # eq_(head.channels, nchan)
    # eq_(head.matrix_size[0], nx)
    # eq_(head.matrix_size[1], ny)
    # eq_(head.matrix_size[2], nz)

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

# TODO: address the following:
# def test_flags():
#     img = ismrmrd.Image()
#     eq_(img.flags, 0)

#     for i in range(1, 65):
#         eq_(img.isFlagSet(i), False)

#     for i in range(1, 65):
#         img.setFlag(i)
#         eq_(img.isFlagSet(i), True)

#     for i in range(1, 65):
#         eq_(img.isFlagSet(i), True)

#     for i in range(1, 65):
#         img.clearFlag(i)
#         eq_(img.isFlagSet(i), False)

#     eq_(img.flags, 0)

#     for i in range(1, 65):
#         img.setFlag(i)
#     img.clearAllFlags()
#     for i in range(1, 65):
#         eq_(img.isFlagSet(i), False)
