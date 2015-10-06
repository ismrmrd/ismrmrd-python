import ctypes
import numpy as np
import copy

from .constants import *

# EncodingCounters
class EncodingCounters(ctypes.Structure):
    _pack_ = 2
    _fields_ = [("kspace_encode_step_1", ctypes.c_uint16),
                ("kspace_encode_step_2", ctypes.c_uint16),
                ("average", ctypes.c_uint16),
                ("slice", ctypes.c_uint16),
                ("contrast", ctypes.c_uint16),
                ("phase", ctypes.c_uint16),
                ("repetition", ctypes.c_uint16),
                ("set", ctypes.c_uint16),
                ("segment", ctypes.c_uint16),
                ("user", ctypes.c_uint16*USER_INTS),]

    def __str__(self):
        retstr = ''
        for field_name, field_type in self._fields_:
            var = getattr(self,field_name)
            if hasattr(var, '_length_'):
                retstr += '%s: %s\n' % (field_name, ', '.join((str(v) for v in var)))
            else:
                retstr += '%s: %s\n' % (field_name, var)
        return retstr
        
# AcquisitionHeader
class AcquisitionHeader(ctypes.Structure):
    _pack_ = 2
    _fields_ = [("version", ctypes.c_uint16),
                ("flags", ctypes.c_uint64),
                ("measurement_uid", ctypes.c_uint32),
                ("scan_counter", ctypes.c_uint32),
                ("acquisition_time_stamp", ctypes.c_uint32),
                ("physiology_time_stamp", ctypes.c_uint32 * PHYS_STAMPS),
                ("number_of_samples", ctypes.c_uint16),
                ("available_channels", ctypes.c_uint16),
                ("active_channels", ctypes.c_uint16),
                ("channel_mask", ctypes.c_uint64 * CHANNEL_MASKS),
                ("discard_pre", ctypes.c_uint16),
                ("discard_post", ctypes.c_uint16),
                ("center_sample", ctypes.c_uint16),
                ("encoding_space_ref", ctypes.c_uint16),
                ("trajectory_dimensions", ctypes.c_uint16),
                ("sample_time_us", ctypes.c_float),
                ("position", ctypes.c_float * POSITION_LENGTH),
                ("read_dir", ctypes.c_float * DIRECTION_LENGTH),
                ("phase_dir", ctypes.c_float * DIRECTION_LENGTH),
                ("slice_dir", ctypes.c_float * DIRECTION_LENGTH),
                ("patient_table_position", ctypes.c_float * POSITION_LENGTH),
                ("idx", EncodingCounters),
                ("user_int", ctypes.c_int32 * USER_INTS),
                ("user_float", ctypes.c_float * USER_FLOATS),]

    def __str__(self):
        retstr = ''
        for field_name, field_type in self._fields_:
            var = getattr(self,field_name)
            if hasattr(var, '_length_'):
                retstr += '%s: %s\n' % (field_name, ', '.join((str(v) for v in var)))
            else:
                retstr += '%s: %s\n' % (field_name, var)
        return retstr
        
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

    #TODO channel mask functions
            
# Acquisition class
class Acquisition(object):
    __readonly = ('number_of_samples', 'active_channels', 'trajectory_dimensions')
    
    def __init__(self, head = None):
        if head is None:
            self.__head = AcquisitionHeader()
            self.__data = np.empty(shape=(1, 0), dtype=np.complex64)
            self.__traj = np.empty(shape=(0, 1), dtype=np.float32)
        else:
            self.__head = AcquisitionHeader.from_buffer_copy(head)
            self.__data = np.empty(shape=(self.__head.active_channels, self.__head.number_of_samples), dtype=np.complex64)
            self.__traj = np.empty(shape=(self.__head.number_of_samples, self.__head.trajectory_dimensions), dtype=np.float32)

        for (field, type) in self.__head._fields_:
            try:
                g = '__get_' + field
                s = '__set_' + field
                setattr(Acquisition, g, self.__getter(field))
                setattr(Acquisition, s, self.__setter(field))
                p = property(getattr(Acquisition, g), getattr(Acquisition, s))
                setattr(Acquisition, field, p)
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
                raise AttributeError(name+" is read-only. Use resize instead.")
        else:
            def fn(self, val):
                self.__head.__setattr__(name, val)

        return fn

    def resize(self, number_of_samples = 0, active_channels = 1, trajectory_dimensions = 0):
        self.__data = np.resize(self.__data, (active_channels, number_of_samples))
        self.__traj = np.resize(self.__traj, (number_of_samples, trajectory_dimensions))
        self.__head.number_of_samples = number_of_samples
        self.__head.active_channels  = active_channels 
        self.__head.trajectory_dimensions = trajectory_dimensions
               
    def getHead(self):
        return copy.deepcopy(self.__head)

    def setHead(self, hdr):
        self.__head = self.__head.__class__.from_buffer_copy(hdr)
        self.resize(self.__head.number_of_samples, self.__head.active_channels, self.__head.trajectory_dimensions)
    
    @property
    def data(self):
        return self.__data.view()

    @property
    def traj(self):
        return self.__traj.view()

    def clearAllFlags(self):
        self.flags = ctypes.c_uint64(0)
        
    def isFlagSet(self,val):
        return self.__head.isFlagSet(val)

    def setFlag(self,val):
        self.__head.setFlag(val)

    def clearFlag(self,val):
        self.__head.clearFlag(val)
        
    def __str__(self):
        retstr = ''
        retstr += 'Header:\n %s\n' % (self.__head)
        retstr += 'Trajectory:\n %s\n' % (self.traj)
        retstr += 'Data:\n %s\n' % (self.data)
        return retstr
 
