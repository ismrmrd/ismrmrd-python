import ctypes
import numpy as np
import copy

from .constants import *

# Image data type lookup function
def get_image_dtype(val):
    if val == DATATYPE_USHORT:
        return np.uint16
    elif val == DATATYPE_SHORT:
        return np.int16
    elif val == DATATYPE_UINT:
        return np.uint32
    elif val == DATATYPE_INT:
        return np.int
    elif val == DATATYPE_FLOAT:
        return np.float32
    elif val == DATATYPE_DOUBLE:
        return np.float64
    elif val == DATATYPE_CXFLOAT:
        return np.complex64
    elif val == DATATYPE_CXDOUBLE:
        return np.complex128
    else:
        raise TypeError("Unknown image data type.")
    

# Image Header
class ImageHeader(ctypes.Structure):
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
                ("attribute_string_len", ctypes.c_uint32),]

    def clearAllFlags(self):
        self.flags = ctypes.c_uint64(0)
        
    def isFlagSet(self,val):
        return ((self.flags & (ctypes.c_uint64(1).value << (val-1))) > 0)

    def setFlag(self,val):
        self.flags |= (ctypes.c_uint64(1).value << (val-1))

    def clearFlag(self,val):
        if self.isFlagSet(val):
            bitmask = (ctypes.c_uint64(1).value << (val-1))
            self.flags -= bitmask

    def __str__(self):
        retstr = ''
        for field_name, field_type in self._fields_:
            var = getattr(self,field_name)
            if hasattr(var, '_length_'):
                retstr += '%s: %s\n' % (field_name, ', '.join((str(v) for v in var)))
            else:
                retstr += '%s: %s\n' % (field_name, var)
        return retstr


# Image class
class Image(object):
    __readonly = ('data_type', 'matrix_size', 'channels', 'attribute_string_len')
    __ignore = ('matrix_size')
    
    def __init__(self, head = None, attribute_string = ""):
        if head is None:
            self.__head = ImageHeader()
            self.__head.data_type = DATATYPE_CXFLOAT
            self.__data = np.empty(shape=(1, 1, 1, 0), dtype=get_image_dtype(DATATYPE_CXFLOAT))
        else:
            self.__head = ImageHeader.from_buffer_copy(head)
            self.__data = np.empty(shape=(self.__head.channels, self.__head.matrix_size[2],
                                          self.__head.matrix_size[1], self.__head.matrix_size[0]),
                                          dtype=get_image_dtype(self.__head.data_type))

        #TODO do we need to check if attribute_string is really a string?
        self.__attribute_string = attribute_string
        if (len(self.__attribute_string) != self.__head.attribute_string_len):
            raise ValueError("attribute_string and head.attribute_string_len are inconsistent.")
        

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
            def fn(self,val):
                raise AttributeError(name+" is read-only.")
        else:
            def fn(self, val):
                self.__head.__setattr__(name, val)

        return fn

    def getHead(self):
        return copy.deepcopy(self.__head)

    def setHead(self, hdr):
        self.__head = self.__head.__class__.from_buffer_copy(hdr)
        self.setDataType(self.__head.data_type)
        self.resize(self.__head.channels, self.__head.matrix_size[2], self.__head.matrix_size[1], self.__head.matrix_size[0])

    def setDataType(self, val):
        self.__data = self.__data.astype(get_image_dtype(val))
        
    def resize(self, nc, nz, ny, nx):
        self.__data = np.resize(self.__data, (nc, nz, ny, nx))

    @property
    def data(self):
        return self.__data.view()

    @property
    def attribute_string(self):
        return self.__attribute_string
    
    @attribute_string.setter
    def attribute_string(self,val):
        self.__attribute_string = str(val)
        self.__head.attribute_string_len = len(self.__attribute_string)
        
    @property
    def matrix_size(self):
        return self.__data.shape[1:4]

    def __str__(self):
        retstr = ''
        retstr += 'Header:\n %s\n' % (self.__head)
        retstr += 'Attribute string:\n %s\n' % (self.attribute_string)
        retstr += 'Data:\n %s\n' % (self.data)
        return retstr
        
