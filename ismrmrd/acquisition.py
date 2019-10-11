import ctypes
import numpy as np
import copy
import io

from .constants import *
from .flags import FlagsMixin
from .equality import EqualityMixin


class EncodingCounters(EqualityMixin, ctypes.Structure):
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
                ("user", ctypes.c_uint16 * USER_INTS)]

    def __str__(self):
        retstr = ''
        for field_name, field_type in self._fields_:
            var = getattr(self, field_name)
            if hasattr(var, '_length_'):
                retstr += '%s: %s\n' % (field_name, ', '.join((str(v) for v in var)))
            else:
                retstr += '%s: %s\n' % (field_name, var)
        return retstr


class AcquisitionHeader(FlagsMixin, EqualityMixin, ctypes.Structure):
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
                ("user_float", ctypes.c_float * USER_FLOATS)]

    def __str__(self):
        retstr = ''
        for field_name, field_type in self._fields_:
            var = getattr(self, field_name)
            if hasattr(var, '_length_'):
                retstr += '%s: %s\n' % (field_name, ', '.join((str(v) for v in var)))
            else:
                retstr += '%s: %s\n' % (field_name, var)
        return retstr


class Acquisition(FlagsMixin):
    __readonly = ('number_of_samples', 'active_channels', 'trajectory_dimensions')

    @staticmethod
    def deserialize_from(read_exactly):

        header_bytes = read_exactly(ctypes.sizeof(AcquisitionHeader))
        acquisition = Acquisition(header_bytes)

        trajectory_bytes = read_exactly(acquisition.number_of_samples *
                                        acquisition.trajectory_dimensions *
                                        ctypes.sizeof(ctypes.c_float))
        data_bytes = read_exactly(acquisition.number_of_samples *
                                  acquisition.active_channels *
                                  ctypes.sizeof(ctypes.c_float * 2))

        trajectory = np.frombuffer(trajectory_bytes, dtype=np.float32)
        data = np.frombuffer(data_bytes, dtype=np.complex64)

        acquisition.traj[:] = trajectory.reshape((acquisition.number_of_samples,
                                                  acquisition.trajectory_dimensions))[:]
        acquisition.data[:] = data.reshape((acquisition.active_channels,
                                            acquisition.number_of_samples))[:]

        return acquisition

    def serialize_into(self, write):
        write(self.__head)
        write(self.__traj.tobytes())
        write(self.__data.tobytes())

    @staticmethod
    def from_bytes(bytelike):
        with io.BytesIO(bytelike) as stream:
            return Acquisition.deserialize_from(stream.read)

    def to_bytes(self):
        with io.BytesIO() as stream:
            self.serialize_into(stream.write)
            return stream.getvalue()

    @staticmethod
    def from_array(data, trajectory=None, **kwargs):

        nchannels, nsamples = data.shape

        if trajectory is None:
            trajectory = np.zeros(shape=(nsamples, 0), dtype=np.float32)

        _, trajectory_dimensions = trajectory.shape

        defaults = {
            'version': 1,
            'number_of_samples': nsamples,
            'active_channels': nchannels,
            'available_channels': nchannels,
            'trajectory_dimensions': trajectory_dimensions
        }

        properties = dict(defaults, **kwargs)

        header = AcquisitionHeader()

        for field in properties:
            setattr(header, field, properties.get(field))

        acquisition = Acquisition(header)
        acquisition.data[:] = data
        acquisition.traj[:] = trajectory

        return acquisition

    def __init__(self, head=None, data=None, trajectory=None):
        def generate_header():
            if head is None:
                if data is None:
                    return AcquisitionHeader()
                else:
                    nchannels, nsamples = data.shape
                    trajectory_dimensions = trajectory.shape[1] if trajectory is not None else 0
                    header = AcquisitionHeader()
                    header.number_of_samples = nsamples
                    header.active_channels = nchannels
                    header.available_channels = nchannels
                    header.trajectory_dimensions = trajectory_dimensions
                    return header
            else:
                if type(head) == AcquisitionHeader:
                    return head
                else:
                    return AcquisitionHeader.from_buffer_copy(head)

        def generate_data_array(header):
            return data if data is not None else np.zeros(shape=(header.active_channels, header.number_of_samples),
                                                          dtype=np.complex64)

        def generate_trajectory_array(header):
            return trajectory if trajectory is not None else np.zeros(
                shape=(header.number_of_samples, header.trajectory_dimensions), dtype=np.float32)

        self.__head = generate_header()

        self.__data = generate_data_array(self.__head)
        self.__traj = generate_trajectory_array(self.__head)

        for (field, _) in self.__head._fields_:
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
            def fn(self, val):
                raise AttributeError(name + " is read-only. Use resize instead.")
        else:
            def fn(self, val):
                self.__head.__setattr__(name, val)

        return fn

    def resize(self, number_of_samples=0, active_channels=1, trajectory_dimensions=0):
        self.__data = np.resize(self.__data, (active_channels, number_of_samples))
        self.__traj = np.resize(self.__traj, (number_of_samples, trajectory_dimensions))
        self.__head.number_of_samples = number_of_samples
        self.__head.active_channels = active_channels
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

    def __str__(self):
        retstr = ''
        retstr += 'Header:\n %s\n' % (self.__head)
        retstr += 'Trajectory:\n %s\n' % (self.traj)
        retstr += 'Data:\n %s\n' % (self.data)
        return retstr

    def __eq__(self, other):
        if not isinstance(other, Acquisition):
            return False

        return all([
            self.__head == other.__head,
            np.array_equal(self.__data, other.__data),
            np.array_equal(self.__traj, other.__traj)
        ])
