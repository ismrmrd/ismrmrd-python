import ctypes
import numpy as np
import copy

# Constants
USER_INTS = 8
USER_FLOATS = 8
PHYS_STAMPS = 3
CHANNEL_MASKS = 16
NDARRAY_MAXDIM = 7
POSITION_LENGTH = 3
DIRECTION_LENGTH = 3

# Acquisition Flags
ACQ_FIRST_IN_ENCODE_STEP1               =  1
ACQ_LAST_IN_ENCODE_STEP1                =  2
ACQ_FIRST_IN_ENCODE_STEP2               =  3
ACQ_LAST_IN_ENCODE_STEP2                =  4
ACQ_FIRST_IN_AVERAGE                    =  5
ACQ_LAST_IN_AVERAGE                     =  6
ACQ_FIRST_IN_SLICE                      =  7
ACQ_LAST_IN_SLICE                       =  8
ACQ_FIRST_IN_CONTRAST                   =  9
ACQ_LAST_IN_CONTRAST                    = 10
ACQ_FIRST_IN_PHASE                      = 11
ACQ_LAST_IN_PHASE                       = 12
ACQ_FIRST_IN_REPETITION                 = 13
ACQ_LAST_IN_REPETITION                  = 14
ACQ_FIRST_IN_SET                        = 15
ACQ_LAST_IN_SET                         = 16
ACQ_FIRST_IN_SEGMENT                    = 17
ACQ_LAST_IN_SEGMENT                     = 18
ACQ_IS_NOISE_MEASUREMENT                = 19
ACQ_IS_PARALLEL_CALIBRATION             = 20
ACQ_IS_PARALLEL_CALIBRATION_AND_IMAGING = 21
ACQ_IS_REVERSE                          = 22
ACQ_IS_NAVIGATION_DATA                  = 23
ACQ_IS_PHASECORR_DATA                   = 24
ACQ_LAST_IN_MEASUREMENT                 = 25
ACQ_IS_HPFEEDBACK_DATA                  = 26
ACQ_IS_DUMMYSCAN_DATA                   = 27
ACQ_IS_RTFEEDBACK_DATA                  = 28
ACQ_IS_SURFACECOILCORRECTIONSCAN_DATA   = 29
ACQ_USER1                               = 57
ACQ_USER2                               = 58
ACQ_USER3                               = 59
ACQ_USER4                               = 60
ACQ_USER5                               = 61
ACQ_USER6                               = 62
ACQ_USER7                               = 63
ACQ_USER8                               = 64

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

    #TODO - pretty print
    #def __repr__(self):
    #    for field_name, field_type in self._fields_:
    #        print field_name, getattr(self, field_name)
        
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

    #TODO pretty print
    #def __repr__(self):
    #    for field_name, field_type in self._fields_:
    #        print field_name, getattr(self, field_name)
        
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
