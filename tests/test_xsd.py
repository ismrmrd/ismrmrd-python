import ismrmrd.xsd
from ismrmrd.xsd.ismrmrdschema import (
    ismrmrdHeader,
    experimentalConditionsType,
    encodingType,
    encodingSpaceType,
    matrixSizeType,
    fieldOfViewMm,
    encodingLimitsType,
    trajectoryType,
)


def make_encoding_space(x, y, z, fov_x, fov_y, fov_z):
    return encodingSpaceType(
        matrixSize=matrixSizeType(x=x, y=y, z=z),
        fieldOfView_mm=fieldOfViewMm(x=fov_x, y=fov_y, z=fov_z),
    )


def make_header():
    return ismrmrdHeader(
        experimentalConditions=experimentalConditionsType(
            H1resonanceFrequency_Hz=128000000,
        ),
        encoding=[
            encodingType(
                encodedSpace=make_encoding_space(256, 256, 1, 300.0, 300.0, 6.0),
                reconSpace=make_encoding_space(256, 256, 1, 300.0, 300.0, 6.0),
                encodingLimits=encodingLimitsType(),
                trajectory=trajectoryType.CARTESIAN,
            )
        ],
    )


def test_construct_header():
    """Constructing ismrmrdHeader and its sub-types using required keyword args should not raise."""
    header = make_header()
    assert header.experimentalConditions.H1resonanceFrequency_Hz == 128000000
    assert len(header.encoding) == 1
    enc = header.encoding[0]
    assert enc.trajectory == trajectoryType.CARTESIAN
    assert enc.encodedSpace.matrixSize.x == 256
    assert enc.encodedSpace.fieldOfView_mm.z == 6.0


def test_header_roundtrip():
    """A header built from constructors should survive a ToXML -> CreateFromDocument round-trip."""
    header = make_header()
    xml = ismrmrd.xsd.ToXML(header)
    reparsed = ismrmrd.xsd.CreateFromDocument(xml)
    assert ismrmrd.xsd.ToXML(reparsed) == xml
