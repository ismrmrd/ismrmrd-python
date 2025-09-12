import sys
from ismrmrd.serialization import ProtocolSerializer, ProtocolDeserializer


def main():
    reader = ProtocolDeserializer(sys.stdin.buffer)
    with ProtocolSerializer(sys.stdout.buffer) as writer:
        for item in reader.deserialize():
            writer.serialize(item)

if __name__ == '__main__':
    main()