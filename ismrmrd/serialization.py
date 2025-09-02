"""
serialization.py

Implements ProtocolSerializer and ProtocolDeserializer for streaming ISMRMRD objects (Acquisition, Image, Waveform, etc.)
"""
import struct
from ismrmrd.acquisition import Acquisition
from ismrmrd.image import Image
from ismrmrd.waveform import Waveform

from enum import IntEnum

class ISMRMRDMessageID(IntEnum):
    UNPEEKED = 0
    CONFIG_FILE = 1
    CONFIG_TEXT = 2
    HEADER = 3
    CLOSE = 4
    TEXT = 5
    ACQUISITION = 1008
    IMAGE = 1022
    WAVEFORM = 1026
    NDARRAY = 1030

class ProtocolSerializer:
    """
    Serializes ISMRMRD objects to a binary stream.
    """
    def __init__(self, stream):
        self.stream = stream

    def serialize(self, obj):
        """
        Serializes an ISMRMRD object and writes to the configured stream.
        """
        if isinstance(obj, Acquisition):
            msg_id = struct.pack('<H', ISMRMRDMessageID.ACQUISITION)
            self.stream.write(msg_id)
            obj.serialize_into(self.stream.write)
        elif isinstance(obj, Image):
            self._serialize_image(obj)
        elif isinstance(obj, Waveform):
            self._serialize_waveform(obj)
        else:
            raise TypeError(f"Unsupported type: {type(obj)}")

    def _serialize_acquisition(self, acq):
        # 1. Prefix with MessageID (uint16_t)
        msg_id = struct.pack('<H', ISMRMRDMessageID.ACQUISITION)
        self.stream.write(msg_id)

        # 2. Serialize AcquisitionHeader
        header_fmt = '<H Q I I I 3I H H H 16Q H H H H H f 3f 3f 3f 3f 3f 8H 8H 8f'
        idx = acq.idx
        header = struct.pack(
            header_fmt,
            acq.version,
            acq.flags,
            acq.measurement_uid,
            acq.scan_counter,
            acq.acquisition_time_stamp,
            *acq.physiology_time_stamp,
            acq.number_of_samples,
            acq.available_channels,
            acq.active_channels,
            *acq.channel_mask,
            acq.discard_pre,
            acq.discard_post,
            acq.center_sample,
            acq.encoding_space_ref,
            acq.trajectory_dimensions,
            acq.sample_time_us,
            *acq.position,
            *acq.read_dir,
            *acq.phase_dir,
            *acq.slice_dir,
            *acq.patient_table_position,
            idx.kspace_encode_step_1,
            idx.kspace_encode_step_2,
            idx.average,
            idx.slice,
            idx.contrast,
            idx.phase,
            idx.repetition,
            idx.set,
            idx.segment,
            *idx.user,
            *acq.user_int,
            *acq.user_float
        )
        self.stream.write(header)

        # 3. Trajectory array (float32)
        if acq.trajectory is not None:
            trajectory = acq.trajectory.astype('float32').tobytes()
            self.stream.write(trajectory)

        # 4. K-space line array (complex float32)
        kspace = acq.data.astype('complex64').tobytes()
        self.stream.write(kspace)

    def _serialize_image(self, img):
        # 1. Prefix with MessageID (uint16_t)
        msg_id = struct.pack('<H', ISMRMRDMessageID.IMAGE)
        self.stream.write(msg_id)

        # 2. Serialize ImageHeader (field order from image.py)
        header_fmt = '<H H Q I 3H 3f H 3f 3f 3f 3f H H H H H I 3I H H H 8i 8f I'
        header = struct.pack(
            header_fmt,
            img.header.version,
            img.header.data_type,
            img.header.flags,
            img.header.measurement_uid,
            *img.header.matrix_size,
            *img.header.field_of_view,
            img.header.channels,
            *img.header.position,
            *img.header.read_dir,
            *img.header.phase_dir,
            *img.header.slice_dir,
            *img.header.patient_table_position,
            img.header.average,
            img.header.slice,
            img.header.contrast,
            img.header.phase,
            img.header.repetition,
            img.header.set,
            img.header.acquisition_time_stamp,
            *img.header.physiology_time_stamp,
            img.header.image_type,
            img.header.image_index,
            img.header.image_series_index,
            *img.header.user_int,
            *img.header.user_float,
            img.header.attribute_string_len
        )
        self.stream.write(header)

        # 3. Image attribute string (length-prefixed)
        attr_bytes = img.attribute_string.encode('utf-8')
        self.stream.write(attr_bytes)

        # 4. Image data
        self.stream.write(img.data.tobytes())

    def _serialize_waveform(self, wf):
        # 1. Prefix with MessageID (uint16_t)
        msg_id = struct.pack('<H', ISMRMRDMessageID.WAVEFORM)
        self.stream.write(msg_id)

        # 2. Serialize WaveformHeader (from waveform.h)
        header_fmt = '<H Q I I I H H f H'
        head = wf.getHead()
        header = struct.pack(
            header_fmt,
            head.version,
            head.flags,
            head.measurement_uid,
            head.scan_counter,
            head.time_stamp,
            head.number_of_samples,
            head.channels,
            head.sample_time_us,
            head.waveform_id
        )
        self.stream.write(header)

        # 3. Waveform array (float32, shape: channels x number_of_samples)
        self.stream.write(wf.data.astype('float32').tobytes())

class ProtocolDeserializer:
    """
    Deserializes binary stream to ISMRMRD objects.
    """
    def __init__(self, stream):
        self.stream = stream

    def deserialize(self):
        """
        Reads from the configured stream and deserializes the next ISMRMRD object.
        """
        msg_id_bytes = self.stream.read(2)
        if not msg_id_bytes or len(msg_id_bytes) < 2:
            raise EOFError("End of stream or incomplete message ID")
        msg_id = struct.unpack('<H', msg_id_bytes)[0]
        if msg_id == ISMRMRDMessageID.ACQUISITION:
            return Acquisition.deserialize_from(self.stream.read)
        elif msg_id == ISMRMRDMessageID.IMAGE:
            return self._deserialize_image()
        elif msg_id == ISMRMRDMessageID.WAVEFORM:
            return self._deserialize_waveform()
        else:
            raise ValueError(f"Unknown MessageID: {msg_id}")

    def _deserialize_acquisition(self):
        # Read and unpack AcquisitionHeader
        header_fmt = '<H Q I I I 3I H H H 16Q H H H H H f 3f 3f 3f 3f 3f 8H 8H 8f'
        header_size = struct.calcsize(header_fmt)
        header_bytes = self.stream.read(header_size)
        if len(header_bytes) < header_size:
            raise EOFError("Incomplete AcquisitionHeader")
        unpacked = struct.unpack(header_fmt, header_bytes)
        # Map unpacked fields to Acquisition and idx
        acq = Acquisition()
        acq.version = unpacked[0]
        acq.flags = unpacked[1]
        acq.measurement_uid = unpacked[2]
        acq.scan_counter = unpacked[3]
        acq.acquisition_time_stamp = unpacked[4]
        acq.physiology_time_stamp = list(unpacked[5:8])
        acq.number_of_samples = unpacked[8]
        acq.available_channels = unpacked[9]
        acq.active_channels = unpacked[10]
        acq.channel_mask = list(unpacked[11:27])
        acq.discard_pre = unpacked[27]
        acq.discard_post = unpacked[28]
        acq.center_sample = unpacked[29]
        acq.encoding_space_ref = unpacked[30]
        acq.trajectory_dimensions = unpacked[31]
        acq.sample_time_us = unpacked[32]
        acq.position = list(unpacked[33:36])
        acq.read_dir = list(unpacked[36:39])
        acq.phase_dir = list(unpacked[39:42])
        acq.slice_dir = list(unpacked[42:45])
        acq.patient_table_position = list(unpacked[45:48])
        # EncodingCounters
        from ismrmrd.acquisition import EncodingCounters
        idx = EncodingCounters()
        idx.kspace_encode_step_1 = unpacked[48]
        idx.kspace_encode_step_2 = unpacked[49]
        idx.average = unpacked[50]
        idx.slice = unpacked[51]
        idx.contrast = unpacked[52]
        idx.phase = unpacked[53]
        idx.repetition = unpacked[54]
        idx.set = unpacked[55]
        idx.segment = unpacked[56]
        idx.user = list(unpacked[57:65])
        acq.idx = idx
        acq.user_int = list(unpacked[65:73])
        acq.user_float = list(unpacked[73:81])

        # Trajectory array
        if acq.trajectory_dimensions > 0:
            traj_size = acq.trajectory_dimensions * acq.number_of_samples * 4
            traj_bytes = self.stream.read(traj_size)
            import numpy as np
            acq.trajectory = np.frombuffer(traj_bytes, dtype='float32').reshape((acq.number_of_samples, acq.trajectory_dimensions))
        else:
            acq.trajectory = None

        # K-space line array
        kspace_size = acq.active_channels * acq.number_of_samples * 8
        kspace_bytes = self.stream.read(kspace_size)
        import numpy as np
        acq.data = np.frombuffer(kspace_bytes, dtype='complex64').reshape((acq.active_channels, acq.number_of_samples))

        return acq

    def _deserialize_image(self):
        # 1. Read ImageHeader
        header_fmt = '<H H Q I 3H 3f H 3f 3f 3f 3f H H H H H I 3I H H H 8i 8f I'
        header_size = struct.calcsize(header_fmt)
        header_bytes = self.stream.read(header_size)
        if len(header_bytes) < header_size:
            raise EOFError("Incomplete ImageHeader")
        unpacked = struct.unpack(header_fmt, header_bytes)
        img = Image()
        img.header = type('ImageHeader', (), {})()
        img.header.version = unpacked[0]
        img.header.data_type = unpacked[1]
        img.header.flags = unpacked[2]
        img.header.measurement_uid = unpacked[3]
        img.header.matrix_size = list(unpacked[4:7])
        img.header.field_of_view = list(unpacked[7:10])
        img.header.channels = unpacked[10]
        img.header.position = list(unpacked[11:14])
        img.header.read_dir = list(unpacked[14:17])
        img.header.phase_dir = list(unpacked[17:20])
        img.header.slice_dir = list(unpacked[20:23])
        img.header.patient_table_position = list(unpacked[23:26])
        img.header.average = unpacked[26]
        img.header.slice = unpacked[27]
        img.header.contrast = unpacked[28]
        img.header.phase = unpacked[29]
        img.header.repetition = unpacked[30]
        img.header.set = unpacked[31]
        img.header.acquisition_time_stamp = unpacked[32]
        img.header.physiology_time_stamp = list(unpacked[33:36])
        img.header.image_type = unpacked[36]
        img.header.image_index = unpacked[37]
        img.header.image_series_index = unpacked[38]
        img.header.user_int = list(unpacked[39:47])
        img.header.user_float = list(unpacked[47:55])
        img.header.attribute_string_len = unpacked[55]
        # 2. Read image attribute string
        attr_len = img.header.attribute_string_len
        attr_bytes = self.stream.read(attr_len)
        img.attribute_string = attr_bytes.decode('utf-8')
        # 3. Read image data
        import numpy as np
        shape = (img.header.channels, img.header.matrix_size[2], img.header.matrix_size[1], img.header.matrix_size[0])
        num_elements = np.prod(shape)
        dtype_map = {
            1: np.uint16,  # USHORT
            2: np.int16,   # SHORT
            3: np.uint32,  # UINT
            4: np.int32,   # INT
            5: np.float32, # FLOAT
            6: np.float64, # DOUBLE
            7: np.complex64, # CXFLOAT
            8: np.complex128 # CXDOUBLE
        }
        dtype = dtype_map.get(img.header.data_type, np.float32)
        data_bytes = self.stream.read(int(num_elements * np.dtype(dtype).itemsize))
        img.data = np.frombuffer(data_bytes, dtype=dtype).reshape(shape)
        return img

    def _deserialize_waveform(self):
        # 1. Read WaveformHeader
        header_fmt = '<H Q I I I H H f H'
        header_size = struct.calcsize(header_fmt)
        header_bytes = self.stream.read(header_size)
        if len(header_bytes) < header_size:
            raise EOFError("Incomplete WaveformHeader")
        unpacked = struct.unpack(header_fmt, header_bytes)
        wf = Waveform()
        wf.header = type('WaveformHeader', (), {})()
        wf.header.version = unpacked[0]
        wf.header.flags = unpacked[1]
        wf.header.measurement_uid = unpacked[2]
        wf.header.scan_counter = unpacked[3]
        wf.header.time_stamp = unpacked[4]
        wf.header.number_of_samples = unpacked[5]
        wf.header.channels = unpacked[6]
        wf.header.sample_time_us = unpacked[7]
        wf.header.waveform_id = unpacked[8]
        # 2. Read waveform array
        arr_size = wf.header.number_of_samples * wf.header.channels * 4
        import numpy as np
        arr_bytes = self.stream.read(arr_size)
        wf.data = np.frombuffer(arr_bytes, dtype='float32').reshape((wf.header.channels, wf.header.number_of_samples))
        return wf
