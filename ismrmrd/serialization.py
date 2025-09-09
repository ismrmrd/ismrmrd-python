"""
Implements ProtocolSerializer and ProtocolDeserializer for streaming ISMRMRD objects (Acquisition, Image, Waveform, etc.)
"""
import struct
from typing import Union, BinaryIO, Any, Generator, cast
import numpy as np

from ismrmrd.acquisition import Acquisition
from ismrmrd.image import Image, get_data_type_from_dtype, get_dtype_from_data_type
from ismrmrd.waveform import Waveform
from ismrmrd.xsd import ismrmrdHeader, CreateFromDocument

from enum import IntEnum

# Type alias for serializable objects
SerializableObject = Union[Acquisition, Image, Waveform, ismrmrdHeader, np.ndarray, str]

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

    def close(self) -> None:
        self.flush()
        if self._owns_stream:
            self._stream.close()

    def __init__(self, stream: Union[BinaryIO, str]) -> None:
        if isinstance(stream, str):
            self._stream = cast(BinaryIO, open(stream, "wb"))
            self._owns_stream = True
        else:
            self._stream = stream
            self._owns_stream = False

    def __enter__(self) -> 'ProtocolSerializer':
        return self

    def __exit__(self, exc_type: Union[type[BaseException], None], exc: Union[BaseException, None], traceback: Any) -> None:
        try:
            self.close()
        except Exception as e:
            if exc is None:
                raise e

    def close(self) -> None:
        self._write_message_id(ISMRMRDMessageID.CLOSE)
        self._stream.flush()
        if self._owns_stream:
            self._stream.close()

    def _write_message_id(self, msgid: ISMRMRDMessageID) -> None:
        self._stream.write(struct.pack('<H', msgid))

    def serialize(self, obj: SerializableObject) -> None:
        """
        Serializes an ISMRMRD object and writes to the configured stream.
        """
        if isinstance(obj, Acquisition):
            self._write_message_id(ISMRMRDMessageID.ACQUISITION)
            obj.serialize_into(self._stream.write)
        elif isinstance(obj, Image):
            self._write_message_id(ISMRMRDMessageID.IMAGE)
            obj.serialize_into(self._stream.write)
        elif isinstance(obj, Waveform):
            self._write_message_id(ISMRMRDMessageID.WAVEFORM)
            obj.serialize_into(self._stream.write)
        elif isinstance(obj, ismrmrdHeader):
            self._write_message_id(ISMRMRDMessageID.HEADER)
            self._serialize_ismrmrd_header(obj)
        elif isinstance(obj, np.ndarray):
            self._write_message_id(ISMRMRDMessageID.NDARRAY)
            self._serialize_ndarray(obj)
        elif isinstance(obj, str):
            self._write_message_id(ISMRMRDMessageID.TEXT)
            self._serialize_text(obj)
        else:
            raise TypeError(f"Unsupported type: {type(obj)}")

    def _serialize_ismrmrd_header(self, header: ismrmrdHeader) -> None:
        xml_bytes = header.toXML().encode('utf-8')
        self._stream.write(struct.pack('<I', len(xml_bytes)))
        self._stream.write(xml_bytes)

    def _serialize_ndarray(self, arr: np.ndarray) -> None:
        ver = 0
        dtype = get_data_type_from_dtype(arr.dtype)
        ndim = arr.ndim
        dims = arr.shape
        self._stream.write(struct.pack('<H H H', dtype, ver, ndim))
        self._stream.write(struct.pack('<' + 'Q' * ndim, *dims))
        self._stream.write(arr.tobytes())

    def _serialize_text(self, text: str) -> None:
        text_bytes = text.encode('utf-8')
        self._stream.write(struct.pack('<I', len(text_bytes)))
        self._stream.write(text_bytes)

class ProtocolDeserializer:
    """
    Deserializes binary stream to ISMRMRD objects.
    """
    def __init__(self, stream: Union[BinaryIO, str]) -> None:
        if isinstance(stream, str):
            self._stream = cast(BinaryIO, open(stream, "rb"))
            self._owns_stream = True
        else:
            self._stream = stream
            self._owns_stream = False

    def __enter__(self) -> 'ProtocolDeserializer':
        return self

    def __exit__(self, exc_type: Union[type[BaseException], None], exc: Union[BaseException, None], traceback: Any) -> None:
        try:
            self.close()
        except Exception as e:
            if exc is None:
                raise e

    def close(self) -> None:
        if self._owns_stream:
            self._stream.close()

    def deserialize(self) -> Generator[SerializableObject, None, None]:
        """
        Reads from the stream, yielding each ISMRMRD object as a generator.
        """
        while True:
            msg_id_bytes = self._stream.read(2)
            if not msg_id_bytes or len(msg_id_bytes) < 2:
                raise EOFError("End of stream or incomplete message ID")
            msg_id = struct.unpack('<H', msg_id_bytes)[0]
            if msg_id == ISMRMRDMessageID.ACQUISITION:
                yield Acquisition.deserialize_from(self._stream.read)
            elif msg_id == ISMRMRDMessageID.IMAGE:
                yield Image.deserialize_from(self._stream.read)
            elif msg_id == ISMRMRDMessageID.WAVEFORM:
                yield Waveform.deserialize_from(self._stream.read)
            elif msg_id == ISMRMRDMessageID.HEADER:
                yield self._deserialize_ismrmrd_header()
            elif msg_id == ISMRMRDMessageID.NDARRAY:
                yield self._deserialize_ndarray()
            elif msg_id == ISMRMRDMessageID.TEXT:
                yield self._deserialize_text()
            elif msg_id == ISMRMRDMessageID.CLOSE:
                return
            else:
                raise ValueError(f"Unknown MessageID: {msg_id}")

    def _deserialize_ismrmrd_header(self) -> ismrmrdHeader:
        length_bytes = self._stream.read(4)
        if len(length_bytes) < 4:
            raise EOFError("Incomplete header length")
        length = struct.unpack('<I', length_bytes)[0]
        header_bytes = self._stream.read(length)
        if len(header_bytes) < length:
            raise EOFError("Incomplete ISMRMRD header")
        return CreateFromDocument(header_bytes)

    def _deserialize_ndarray(self) -> np.ndarray:
        header_fmt = '<H H H'
        header_size = struct.calcsize(header_fmt)
        header_bytes = self._stream.read(header_size)
        if len(header_bytes) < header_size:
            raise EOFError("Incomplete NDArray header")
        data_type, ver, ndim = struct.unpack(header_fmt, header_bytes)

        dims = []
        for _ in range(ndim):
            dim_bytes = self._stream.read(8)
            if len(dim_bytes) < 8:
                raise EOFError("Incomplete NDArray dimensions")
            dims.append(struct.unpack('<Q', dim_bytes)[0])

        nentries = np.prod(dims)
        dtype = get_dtype_from_data_type(data_type)
        nbytes = nentries * dtype.itemsize
        data_bytes = self._stream.read(nbytes)
        if len(data_bytes) < nbytes:
            raise EOFError("Incomplete NDArray data")

        arr = np.frombuffer(data_bytes, dtype=dtype).reshape(dims)
        return arr

    def _deserialize_text(self) -> str:
        length_bytes = self._stream.read(4)
        if len(length_bytes) < 4:
            raise EOFError("Incomplete text length")
        length = struct.unpack('<I', length_bytes)[0]
        text_bytes = self._stream.read(length)
        if len(text_bytes) < length:
            raise EOFError("Incomplete text data")
        return str(text_bytes, 'utf-8')
