from .ismrmrdschema import ismrmrdHeader

from xsdata.formats.dataclass.parsers import XmlParser
from xsdata.formats.dataclass.parsers.config import ParserConfig

from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig
import xml.dom.minidom as md

def CreateFromDocument(document):
    parser = XmlParser(config=ParserConfig(fail_on_unknown_properties=True))
    if isinstance(document,str):
        return parser.from_string(document,ismrmrdHeader)
    return parser.from_bytes(document,ismrmrdHeader)


def ToXML(header: ismrmrdHeader , encoding='ascii'):
    config = SerializerConfig(encoding=encoding,pretty_print=True)
    serializer = XmlSerializer(config)
    return serializer.render(header,ns_map={"":"http://www.ismrm.org/ISMRMRD"})

def ToDOM(header: ismrmrdHeader):
    return md.parseString(ToXML(header))


ismrmrdHeader.toXML = ToXML
ismrmrdHeader.toDOM = ToDOM