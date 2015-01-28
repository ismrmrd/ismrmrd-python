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

# AcquisitionHeader
class AcquisitionHeader(ctypes.Structure):
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
        
class Acquisition(object):
    # Acquisition class
    def __init__(self):
        self.__head = AcquisitionHeader()
        self.__data = np.empty(shape=(1, 0), dtype=np.complex64)
        self.__traj = np.empty(shape=(0, 1), dtype=np.float32)
        
    @property
    def number_of_samples(self):
        return self.__head.number_of_samples

    @property
    def active_channels(self):
        return self.__head.active_channels

    @property
    def trajectory_dimensions(self):
        return self.__head.trajectory_dimensions

    @property
    def version(self):
        return self.__head.version
    @version.setter
    def version(self, value):
        self.__head.version = value

    def resize(self, number_of_samples = 0, active_channels = 1, trajectory_dimensions = 0):
        self.__data = np.resize(self.__data, (active_channels, number_of_samples))
        self.__traj = np.resize(self.__traj, (number_of_samples, trajectory_dimensions))
        self.__head.number_of_samples = number_of_samples
        self.__head.active_channels  = active_channels 
        self.__head.trajectory_dimensions = trajectory_dimensions
               
    def getHead(self):
        return copy.deepcopy(self.__head)

    def setHead(self, hdr):
        self.__head = copy.deepcopy(hdr)
        self.resize(hdr.number_of_samples, hdr.active_channels, hdr.trajectory_dimensions)
    
    @property
    def data(self):
        return self.__data.view()

    @property
    def traj(self):
        return self.__traj.view()
