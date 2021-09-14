from ismrmrd.meta import Meta
import itertools
import ctypes
import numpy as np
import copy
import io
import warnings
warnings.simplefilter('default')

from .acquisition import Acquisition
from .flags import FlagsMixin
from .equality import EqualityMixin
from .constants import *

dtype_mapping = {
    DATATYPE_USHORT: np.dtype('uint16'),
    DATATYPE_SHORT: np.dtype('int16'),
    DATATYPE_UINT: np.dtype('uint32'),
    DATATYPE_INT: np.dtype('int'),
    DATATYPE_FLOAT: np.dtype('float32'),
    DATATYPE_DOUBLE: np.dtype('float64'),
    DATATYPE_CXFLOAT: np.dtype('complex64'),
    DATATYPE_CXDOUBLE: np.dtype('complex128')
}
inverse_dtype_mapping = {dtype_mapping.get(k): k for k in dtype_mapping}


def get_dtype_from_data_type(val):
    dtype = dtype_mapping.get(val)
    if dtype is None:
        raise TypeError("Unknown image data type: " + str(val))
    return dtype


def get_data_type_from_dtype(dtype):
    type = inverse_dtype_mapping.get(dtype)
    if type is None:
        raise TypeError("Datatype not supported: " + str(dtype))
    return type


# Image Header
class ImageHeader(FlagsMixin, EqualityMixin, ctypes.Structure):
    _pack_ = 2
    _fields_ = [("version", ctypes.c_uint16),
                ("data_type", ctypes.c_uint16),
                ("flags", ctypes.c_uint64),
                ("measurement_uid", ctypes.c_uint32),
                ("matrix_size", ctypes.c_uint16 * POSITION_LENGTH),
                ("field_of_view", ctypes.c_float * POSITION_LENGTH),
                ("channels", ctypes.c_uint16),
                ("position", ctypes.c_float * POSITION_LENGTH),
                ("read_dir", ctypes.c_float * DIRECTION_LENGTH),
                ("phase_dir", ctypes.c_float * DIRECTION_LENGTH),
                ("slice_dir", ctypes.c_float * DIRECTION_LENGTH),
                ("patient_table_position", ctypes.c_float * POSITION_LENGTH),
                ("average", ctypes.c_uint16),
                ("slice", ctypes.c_uint16),
                ("contrast", ctypes.c_uint16),
                ("phase", ctypes.c_uint16),
                ("repetition", ctypes.c_uint16),
                ("set", ctypes.c_uint16),
                ("acquisition_time_stamp", ctypes.c_uint32),
                ("physiology_time_stamp", ctypes.c_uint32 * PHYS_STAMPS),
                ("image_type", ctypes.c_uint16),
                ("image_index", ctypes.c_uint16),
                ("image_series_index", ctypes.c_uint16),
                ("user_int", ctypes.c_int32 * USER_INTS),
                ("user_float", ctypes.c_float * USER_FLOATS),
                ("attribute_string_len", ctypes.c_uint32), ]

    @staticmethod
    def from_acquisition(acquisition, **kwargs):

        header = ImageHeader()

        # The value of these fields is copied over from the acquisition header.
        acquisition_fields = [
            'version',
            'measurement_uid',
            'position',
            'read_dir',
            'phase_dir',
            'slice_dir',
            'patient_table_position',
            'acquisition_time_stamp',
            'physiology_time_stamp',
            'user_int',
            'user_float'
        ]

        for field in acquisition_fields:
            setattr(header, field, getattr(acquisition, field))

        idx_fields = ['average', 'slice', 'contrast', 'phase', 'repetition', 'set']
        for field in idx_fields:
            setattr(header, field, getattr(acquisition.idx, field))

        for field in kwargs:
            setattr(header, field, kwargs.get(field))

        return header

    def __str__(self):
        retstr = ''
        for field_name, field_type in self._fields_:
            var = getattr(self, field_name)
            if hasattr(var, '_length_'):
                retstr += '%s: %s\n' % (field_name, ', '.join((str(v) for v in var)))
            else:
                retstr += '%s: %s\n' % (field_name, var)
        return retstr


# Image class
class Image(FlagsMixin):
    __readonly = ('data_type', 'matrix_size', 'channels')
    __ignore = ('matrix_size','attribute_string_len')

    @staticmethod
    def deserialize_from(read_exactly):

        header_bytes = read_exactly(ctypes.sizeof(ImageHeader))
        attribute_length_bytes = read_exactly(ctypes.sizeof(ctypes.c_uint64))
        attribute_length = ctypes.c_uint64.from_buffer_copy(attribute_length_bytes)
        attribute_bytes = read_exactly(attribute_length.value).rstrip(b'\0')

        image = Image(header_bytes, attribute_bytes.decode('utf-8'))

        def calculate_number_of_entries(nchannels, xs, ys, zs):
            return nchannels * xs * ys * zs

        nentries = calculate_number_of_entries(image.channels, *image.matrix_size)
        nbytes = nentries * get_dtype_from_data_type(image.data_type).itemsize

        data_bytes = read_exactly(nbytes)

        image.data.ravel()[:] = np.frombuffer(data_bytes, dtype=get_dtype_from_data_type(image.data_type))

        return image

    def serialize_into(self, write):

        attribute_bytes = self.attribute_string.encode('utf-8')
        self.__head.attribute_string_len = len(attribute_bytes)

        write(self.__head)

        write(ctypes.c_uint64(len(attribute_bytes)))
        write(attribute_bytes)

        write(self.__data.tobytes())

    @staticmethod
    def from_bytes(bytelike):
        with io.BytesIO(bytelike) as stream:
            return Image.deserialize_from(stream.read)

    def to_bytes(self):
        with io.BytesIO() as stream:
            self.serialize_into(stream.write)
            return stream.getvalue()

    @staticmethod
    def from_array(array, acquisition=Acquisition(), transpose=True, **kwargs):

        def input_shape_to_header_format(array):
            def with_defaults(first=1, second=1, third=1, nchannels=1):
                return nchannels, (first, second, third)

            return with_defaults(*reversed(array.shape))

        def header_format_to_resize_shape(nchannels, first, second, third):
            return nchannels, third, second, first

        if transpose:
            warnings.warn(
                "The default behavior of this function is currently column-major which " +
                "is inconsistent with numpy using row-major by default. In a future " +
                "version this will be changed. Please switch to setting transpose in " +
                "this function to false to switch to the new behavior.",
                 PendingDeprecationWarning
            )
            array = array.transpose()

        nchannels, matrix_size = input_shape_to_header_format(array)

        image_properties = {
            'version': 1,
            'data_type': get_data_type_from_dtype(array.dtype),
            'channels': nchannels,
            'matrix_size': matrix_size
        }

        header = ImageHeader.from_acquisition(acquisition, **dict(image_properties, **kwargs))
        image = Image(head=header)

        image.data[:] = np.resize(array, header_format_to_resize_shape(nchannels, *matrix_size))

        return image

    def __init__(self, head=None, attribute_string=None, meta=None):
        if head is None:
            self.__head = ImageHeader()
            self.__head.data_type = DATATYPE_CXFLOAT
            self.__data = np.empty(shape=(1, 1, 1, 0), dtype=get_dtype_from_data_type(DATATYPE_CXFLOAT))
        else:
            self.__head = ImageHeader.from_buffer_copy(head)
            self.__data = np.empty(shape=(self.__head.channels, self.__head.matrix_size[2],
                                          self.__head.matrix_size[1], self.__head.matrix_size[0]),
                                   dtype=get_dtype_from_data_type(self.__head.data_type))

        if attribute_string is not None:
            if meta is not None:
                raise RuntimeError("Attribute string and meta cannot be set simulatnously.")
            self.__meta = Meta.deserialize(attribute_string)
        elif meta is not None:
            self.__meta = meta
        else:
            self.__meta = Meta()

            

        for (field, type) in self.__head._fields_:
            if field in self.__ignore:
                continue
            else:
                try:
                    g = '__get_' + field
                    s = '__set_' + field
                    setattr(Image, g, self.__getter(field))
                    setattr(Image, s, self.__setter(field))
                    p = property(getattr(Image, g), getattr(Image, s))
                    setattr(Image, field, p)
                except TypeError:
                    # e.g. if key is an `int`, skip it
                    pass

    def __getter(self, name):
        if name in self.__readonly:
            def fn(self):
                return copy.copy(self.__head.__getattribute__(name))
        else:
            def fn(self):
                return self.__head.__getattribute__(name)
        return fn

    def __setter(self, name):
        if name in self.__readonly:
            def fn(self, val):
                raise AttributeError(name + " is read-only.")
        else:
            def fn(self, val):
                self.__head.__setattr__(name, val)

        return fn

    def getHead(self):
        return copy.deepcopy(self.__head)

    def setHead(self, hdr):
        self.__head = self.__head.__class__.from_buffer_copy(hdr)
        self.setDataType(self.__head.data_type)
        self.resize(self.__head.channels, self.__head.matrix_size[2], self.__head.matrix_size[1],
                    self.__head.matrix_size[0])

    def setDataType(self, val):
        self.__data = self.__data.astype(get_dtype_from_data_type(val))

    def resize(self, nc, nz, ny, nx):
        self.__data = np.resize(self.__data, (nc, nz, ny, nx))

    @property
    def data(self):
        return self.__data.view()

    @property
    def attribute_string(self):
        return self.__meta.serialize()

    @attribute_string.setter
    def attribute_string(self, val):
        self.__meta = Meta.deserialize(val)

    @property
    def meta(self):
        return self.__meta

    @meta.setter
    def meta(self,val):
        if type(val) == Meta:
            self.__meta = val
        elif type(val) == dict:
            self.__meta = Meta()
            self.__meta.update(val)
        else:
            raise RuntimeError("meta must be of type Meta or dict")

    @property
    def matrix_size(self):
        return self.__data.shape[1:4]
        
    @property
    def attribute_string_len(self):
        return len(self.attribute_string)

    def __str__(self):
        return "Header:\n {}\nAttribute string:\n {}\nData:\n {}\n".format(self.__head, self.__attribute_string,
                                                                           self.__data)

    def __eq__(self, other):
        if not isinstance(other, Image):
            return False

        return all([
            self.__head == other.__head,
            np.array_equal(self.__data, other.__data),
            np.array_equal(self.__attribute_string, other.__attribute_string)
        ])
