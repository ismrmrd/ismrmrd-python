import ctypes
import numpy as np
import copy


class WaveformHeader(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("version", ctypes.c_uint16),
                ("__alignment_bits",ctypes.c_uint8 * 6), #Ctypes flatly refuses to replicate the hdf5 data layout, so instead we have pack bits.
                ("flags", ctypes.c_uint64),
                ("measurement_uid", ctypes.c_uint32),
                ("scan_counter", ctypes.c_uint32),
                ("time_stamp", ctypes.c_uint32),
                ("number_of_samples", ctypes.c_uint16),
                ("channels", ctypes.c_uint16),
                ("sample_time_us", ctypes.c_float),
                ("waveform_id", ctypes.c_uint16),
                ]

    def __str__(self):
        retstr = ''
        for field_name, field_type in self._fields_:
            if field_name == "__alignment_bits":
                continue
            var = getattr(self, field_name)
            if hasattr(var, '_length_'):
                retstr += '%s: %s\n' % (field_name, ', '.join((str(v) for v in var)))
            else:
                retstr += '%s: %s\n' % (field_name, var)
        return retstr

    def clearAllFlags(self):
        self.flags = ctypes.c_uint64(0)

    def isFlagSet(self, val):
        return ((self.flags & (ctypes.c_uint64(1).value << (val - 1))) > 0)

    def setFlag(self, val):
        self.flags |= (ctypes.c_uint64(1).value << (val - 1))

    def clearFlag(self, val):
        if self.isFlagSet(val):
            bitmask = (ctypes.c_uint64(1).value << (val - 1))
            self.flags -= bitmask

    # TODO channel mask functions


class Waveform(object):
    __readonly = ('number_of_samples', 'channels')

    def __init__(self, head = None):
        if head is None:
            self.__head = WaveformHeader()
            self.__data = np.empty(shape=(1, 0), dtype=np.uint32)
        else:
            self.__head = WaveformHeader.from_buffer_copy(head)
            self.__data = np.empty(shape=(self.__head.channels, self.__head.number_of_samples), dtype=np.uint32)

        for (field, type) in self.__head._fields_:
            try:
                g = '__get_' + field
                s = '__set_' + field
                setattr(Waveform, g, self.__getter(field))
                setattr(Waveform, s, self.__setter(field))
                p = property(getattr(Waveform, g), getattr(Waveform, s))
                setattr(Waveform, field, p)
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

    def resize(self, number_of_samples = 0, channels= 1):
        self.__data = np.resize(self.__data, (channels, number_of_samples))
        self.__head.number_of_samples = number_of_samples
        self.__head.channels  = channels

    def getHead(self):
        return copy.deepcopy(self.__head)

    def setHead(self, hdr):
        self.__head = self.__head.__class__.from_buffer_copy(hdr)
        self.resize(self.__head.number_of_samples, self.__head.active_channels )

    @property
    def data(self):
        return self.__data.view()

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

