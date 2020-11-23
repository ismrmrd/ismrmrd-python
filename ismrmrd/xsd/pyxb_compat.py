from .ismrmrdschema import ismrmrdHeader

from xsdata.formats.dataclass.parsers import XmlParser
from xsdata.formats.dataclass.parsers.config import ParserConfig

from xsdata.formats.dataclass.serializers import XmlSerializer

def CreateFromDocument(document):
    parser = XmlParser(config=ParserConfig(fail_on_unknown_properties=True))
    if isinstance(document,str):
        return parser.from_string(document,ismrmrdHeader)
    return parser.from_bytes(document,ismrmrdHeader)


def ToXML(header : ismrmrdHeader, encoding = 'ascii'):
    serializer = XmlSerializer(encoding=encoding, pretty_print=True)
    return serializer.render(header)
