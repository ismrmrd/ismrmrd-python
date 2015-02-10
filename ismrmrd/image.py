import ctypes
import numpy as np
import copy

from .constants import *

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
        self.flags = 0L
        
    def isFlagSet(self,val):
        return ((self.flags & (1L << (val-1))) > 0)

    def setFlag(self,val):
        self.flags |= (1L << (val-1))

    def clearFlag(self,val):
        if self.isFlagSet(val):
            bitmask = (1L << (val-1))
            self.flags -= bitmask

    #TODO - pretty print
    #def __repr__(self):
    #    for field_name, field_type in self._fields_:
    #        print field_name, getattr(self, field_name)

## /**
##  *  An individual Image
##  *  @ingroup capi
##  */
## typedef struct ISMRMRD_Image {
##     ISMRMRD_ImageHeader head;
##     char *attribute_string;
##     void *data;
## } ISMRMRD_Image;
