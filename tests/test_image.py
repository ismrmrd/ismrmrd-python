import ismrmrd
import ctypes
import numpy as np

import nose.tools
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


@nose.tools.raises(AttributeError)
def test_read_only_fields():
    img = ismrmrd.Image()

    for field in ['data_type', 'matrix_size', 'channels', 'attribute_string_len']:
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

    eq_(img.data.shape, (nchan, nz, ny, nx))
    eq_(img.data_type, ismrmrd.DATATYPE_CXDOUBLE)
    eq_(img.data.dtype, np.complex128)


def test_resize():
    pass

def test_flags():
    pass


### HEADER
# from_acquisition - defaults
# from_acquisition - initialize with acquisition
# from_acquisition - initialize with kwargs

### IMAGE
## Initialization
# from_array - initialize with acquisition
# from_array - initialize with array
# from_array - initialize with acquisition and array
# from_array - With various dim input array:
#   - 2d
#   - 3d
#   - 2d + channels
#   - 3d + channels
## Serialization
# deserialize_from
# serialize_to
# from_bytes
# to_bytes
