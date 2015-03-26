import ismrmrd
import xml.etree.ElementTree as ET

XML = """<?xml version="1.0"?>
<ismrmrdMeta>
  <meta>
    <name>pi</name>
    <value>3.14159265</value>
  </meta>

  <meta>
    <name>extra</name>
    <value>Hello, World!</value>
  </meta>

  <meta>
    <name>extra</name>
    <value>654321</value>
  </meta>

  <meta>
    <name>extra</name>
    <value>1.234</value>
    <value>67890</value>
    <value>foobar</value>
  </meta>

  <meta>
    <name>when</name>
    <value>2015-03-21, Sat March 2015</value>
    <value>1426933800</value>
  </meta>
</ismrmrdMeta>"""

META = {
        'pi': '3.14159265',
        'when': ['2015-03-21, Sat March 2015', '1426933800'],
        'extra': ['Hello, World!', '654321', '1.234', '67890', 'foobar']
        }

def xml_equivalent(xml1, xml2):
    root1 = ET.fromstring(xml1)
    root2 = ET.fromstring(xml2)

    assert root1.tag == root2.tag
    children1 = root.findall('meta')
    children2 = root.findall('meta')

def test_serialize():
    meta = ismrmrd.Meta(META)
    xml = meta.serialize()

    root = ET.fromstring(xml)
    assert root.tag == 'ismrmrdMeta'
    children = root.findall('meta')

    # check that all expected Name-Value pairs can be found
    for k, v in META.items():
        values = None
        for child in children:
            name = child.find('name')
            assert name is not None
            _values = child.findall('value')
            assert _values is not None
            if name.text == k:
                # found! sort it for later!
                values = [x.text for x in _values]
                break

        assert values is not None

        # make the META value a list
        if type(v) != list:
            v = [v]
        # sort both lists for simpler comparison
        v = sorted([str(x) for x in v])
        values = sorted(values)
        assert v == values


def test_deserialize():
    meta = ismrmrd.Meta.deserialize(XML)
    # dicts should be equivalent
    assert meta == META
