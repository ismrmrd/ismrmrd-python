import ctypes
import numpy as np
import copy
import io

from .flags import FlagsMixin
from .equality import EqualityMixin


class WaveformHeader(FlagsMixin, EqualityMixin, ctypes.Structure):
    _pack_ = 8
    _fields_ = [("version", ctypes.c_uint16),
                ("flags", ctypes.c_uint64),
                ("measurement_uid", ctypes.c_uint32),
                ("scan_counter", ctypes.c_uint32),
                ("time_stamp", ctypes.c_uint32),
                ("number_of_samples", ctypes.c_uint16),
                ("channels", ctypes.c_uint16),
                ("sample_time_us", ctypes.c_float),
                ("waveform_id", ctypes.c_uint16)]

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


class Waveform(FlagsMixin):
    __readonly = ('number_of_samples', 'channels')

    @staticmethod
    def deserialize_from(read_exactly):

        header_bytes = read_exactly(ctypes.sizeof(WaveformHeader))
        waveform = Waveform(header_bytes)

        data_bytes = read_exactly(waveform.channels *
                                  waveform.number_of_samples *
                                  ctypes.sizeof(ctypes.c_uint32))

        waveform.data.ravel()[:] = np.frombuffer(data_bytes, dtype=np.uint32)

        return waveform

    def serialize_into(self, write):
        write(self.__head)
        write(self.__data.tobytes())

    @staticmethod
    def from_bytes(bytelike):
        with io.BytesIO(bytelike) as stream:
            return Waveform.deserialize_from(stream.read)

    def to_bytes(self):
        with io.BytesIO() as stream:
            self.serialize_into(stream.write)
            return stream.getvalue()


    @staticmethod
    def from_array(data, **kwargs):

        channels, nsamples = data.shape

        array_data = {
            'version': 1,
            'channels': channels,
            'number_of_samples': nsamples
        }

        header = WaveformHeader()

        properties = dict(array_data, **kwargs)

        for field in properties:
            setattr(header, field, properties.get(field))

        waveform = Waveform(header)
        waveform.data[:] = data

        return waveform

    def __init__(self, head=None, data=None):
        if head is None:
            self.__head = WaveformHeader()
            self.__data = np.empty(shape=(1, 0), dtype=np.uint32)
        else:
            self.__head = WaveformHeader.from_buffer_copy(head)
            self.__data = np.empty(shape=(self.__head.channels, self.__head.number_of_samples), dtype=np.uint32)

            if data is not None:
                self.data[:] = data.reshape((self.__head.channels,self.__head.number_of_samples), order="C")

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
            def fn(self, val):
                raise AttributeError(name+" is read-only. Use resize instead.")
        else:
            def fn(self, val):
                self.__head.__setattr__(name, val)

        return fn

    def resize(self, number_of_samples=0, channels=1):
        self.__data = np.resize(self.__data, (channels, number_of_samples))
        self.__head.number_of_samples = number_of_samples
        self.__head.channels = channels

    def getHead(self):
        return copy.deepcopy(self.__head)

    def setHead(self, hdr):
        self.__head = self.__head.__class__.from_buffer_copy(hdr)
        self.resize(self.__head.number_of_samples, self.__head.active_channels)

    @property
    def data(self):
        return self.__data.view()

    def __str__(self):
        return "Header:\n {}\nData:\n {}\n".format(self.__head, self.__data)

    def __eq__(self, other):
        if not isinstance(other, Waveform):
            return False

        return all([
            self.__head == other.__head,
            np.array_equal(self.__data, other.__data)
        ])
