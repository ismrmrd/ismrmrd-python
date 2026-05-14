from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from xsdata.models.datatype import XmlDate, XmlTime

__NAMESPACE__ = "http://www.ismrm.org/ISMRMRD"


@dataclass(kw_only=True)
class accelerationFactorType:
    kspace_encoding_step_1: int = field(
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    kspace_encoding_step_2: int = field(
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )


class calibrationModeType(Enum):
    EMBEDDED = "embedded"
    INTERLEAVED = "interleaved"
    SEPARATE = "separate"
    EXTERNAL = "external"
    OTHER = "other"


@dataclass(kw_only=True)
class coilLabelType:
    coilNumber: int = field(
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    coilName: str = field(
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )


class diffusionDimensionType(Enum):
    AVERAGE = "average"
    CONTRAST = "contrast"
    PHASE = "phase"
    REPETITION = "repetition"
    SET = "set"
    SEGMENT = "segment"
    USER_0 = "user_0"
    USER_1 = "user_1"
    USER_2 = "user_2"
    USER_3 = "user_3"
    USER_4 = "user_4"
    USER_5 = "user_5"
    USER_6 = "user_6"
    USER_7 = "user_7"


@dataclass(kw_only=True)
class experimentalConditionsType:
    H1resonanceFrequency_Hz: int = field(
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )


@dataclass(kw_only=True)
class fieldOfViewMm:
    class Meta:
        name = "fieldOfView_mm"

    x: float = field(
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    y: float = field(
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    z: float = field(
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )


@dataclass(kw_only=True)
class gradientDirectionType:
    rl: float = field(
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    ap: float = field(
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    fh: float = field(
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )


class interleavingDimensionType(Enum):
    PHASE = "phase"
    REPETITION = "repetition"
    CONTRAST = "contrast"
    AVERAGE = "average"
    OTHER = "other"


@dataclass(kw_only=True)
class limitType:
    minimum: int = field(
        default=0,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    maximum: int = field(
        default=0,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    center: int = field(
        default=0,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )


@dataclass(kw_only=True)
class matrixSizeType:
    x: int = field(
        default=1,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    y: int = field(
        default=1,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    z: int = field(
        default=1,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )


@dataclass(kw_only=True)
class measurementDependencyType:
    dependencyType: str = field(
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    measurementID: str = field(
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )


class multibandCalibrationType(Enum):
    SEPARABLE2_D = "separable2D"
    FULL3_D = "full3D"
    OTHER = "other"


@dataclass(kw_only=True)
class multibandSpacingType:
    dZ: list[float] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
            "min_occurs": 1,
        },
    )


class patientPositionType(Enum):
    HFP = "HFP"
    HFS = "HFS"
    HFDR = "HFDR"
    HFDL = "HFDL"
    FFP = "FFP"
    FFS = "FFS"
    FFDR = "FFDR"
    FFDL = "FFDL"


@dataclass(kw_only=True)
class referencedImageSequenceType:
    referencedSOPInstanceUID: list[str] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )


@dataclass(kw_only=True)
class studyInformationType:
    studyDate: None | XmlDate = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    studyTime: None | XmlTime = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    studyID: None | str = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    accessionNumber: None | int = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    referringPhysicianName: None | str = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    studyDescription: None | str = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    studyInstanceUID: None | str = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    bodyPartExamined: None | str = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )


@dataclass(kw_only=True)
class subjectInformationType:
    patientName: None | str = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    patientWeight_kg: None | float = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    patientHeight_m: None | float = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    patientID: None | str = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    patientBirthdate: None | XmlDate = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    patientGender: None | str = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
            "pattern": r"[MFO]",
        },
    )


@dataclass(kw_only=True)
class threeDimensionalFloat:
    x: float = field(
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    y: float = field(
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    z: float = field(
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )


class trajectoryType(Enum):
    CARTESIAN = "cartesian"
    EPI = "epi"
    RADIAL = "radial"
    GOLDENANGLE = "goldenangle"
    SPIRAL = "spiral"
    OTHER = "other"


@dataclass(kw_only=True)
class userParameterBase64Type:
    name: str = field(
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    value: bytes = field(
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
            "format": "base64",
        }
    )


@dataclass(kw_only=True)
class userParameterDoubleType:
    name: str = field(
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    value: float = field(
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )


@dataclass(kw_only=True)
class userParameterLongType:
    name: str = field(
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    value: int = field(
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )


@dataclass(kw_only=True)
class userParameterStringType:
    name: str = field(
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    value: str = field(
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )


class waveformInformationTypeWaveformType(Enum):
    ECG = "ecg"
    PULSE = "pulse"
    RESPIRATORY = "respiratory"
    TRIGGER = "trigger"
    GRADIENTWAVEFORM = "gradientwaveform"
    OTHER = "other"


@dataclass(kw_only=True)
class acquisitionSystemInformationType:
    systemVendor: None | str = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    systemModel: None | str = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    systemFieldStrength_T: None | float = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    relativeReceiverNoiseBandwidth: None | float = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    receiverChannels: None | int = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    coilLabel: list[coilLabelType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    institutionName: None | str = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    stationName: None | str = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    deviceID: None | str = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    deviceSerialNumber: None | str = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )


@dataclass(kw_only=True)
class diffusionType:
    gradientDirection: gradientDirectionType = field(
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    bvalue: float = field(
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )


@dataclass(kw_only=True)
class encodingLimitsType:
    kspace_encoding_step_0: None | limitType = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    kspace_encoding_step_1: None | limitType = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    kspace_encoding_step_2: None | limitType = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    average: None | limitType = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    slice: None | limitType = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    contrast: None | limitType = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    phase: None | limitType = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    repetition: None | limitType = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    set: None | limitType = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    segment: None | limitType = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    user_0: None | limitType = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    user_1: None | limitType = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    user_2: None | limitType = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    user_3: None | limitType = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    user_4: None | limitType = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    user_5: None | limitType = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    user_6: None | limitType = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    user_7: None | limitType = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )


@dataclass(kw_only=True)
class encodingSpaceType:
    matrixSize: matrixSizeType = field(
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    fieldOfView_mm: fieldOfViewMm = field(
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )


@dataclass(kw_only=True)
class measurementInformationType:
    measurementID: None | str = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    seriesDate: None | XmlDate = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    seriesTime: None | XmlTime = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    patientPosition: patientPositionType = field(
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    relativeTablePosition: None | threeDimensionalFloat = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    initialSeriesNumber: None | int = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    protocolName: None | str = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    sequenceName: None | str = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    seriesDescription: None | str = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    measurementDependency: list[measurementDependencyType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    seriesInstanceUIDRoot: None | str = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    frameOfReferenceUID: None | str = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    referencedImageSequence: None | referencedImageSequenceType = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )


@dataclass(kw_only=True)
class multibandType:
    spacing: list[multibandSpacingType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
            "min_occurs": 1,
        },
    )
    deltaKz: float = field(
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    multiband_factor: int = field(
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    calibration: multibandCalibrationType = field(
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    calibration_encoding: int = field(
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )


@dataclass(kw_only=True)
class trajectoryDescriptionType:
    identifier: str = field(
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    userParameterLong: list[userParameterLongType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    userParameterDouble: list[userParameterDoubleType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    userParameterString: list[userParameterStringType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    comment: None | str = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )


@dataclass(kw_only=True)
class userParametersType:
    userParameterLong: list[userParameterLongType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    userParameterDouble: list[userParameterDoubleType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    userParameterString: list[userParameterStringType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    userParameterBase64: list[userParameterBase64Type] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )


@dataclass(kw_only=True)
class parallelImagingType:
    accelerationFactor: accelerationFactorType = field(
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    calibrationMode: None | calibrationModeType = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    interleavingDimension: None | interleavingDimensionType = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    multiband: None | multibandType = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )


@dataclass(kw_only=True)
class sequenceParametersType:
    TR: list[float] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    TE: list[float] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    TI: list[float] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    flipAngle_deg: list[float] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    sequence_type: None | str = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    echo_spacing: list[float] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    diffusionDimension: None | diffusionDimensionType = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    diffusion: list[diffusionType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    diffusionScheme: None | str = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )


@dataclass(kw_only=True)
class waveformInformationType:
    waveformName: str = field(
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    waveformType: waveformInformationTypeWaveformType = field(
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    userParameters: userParametersType = field(
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )


@dataclass(kw_only=True)
class encodingType:
    encodedSpace: encodingSpaceType = field(
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    reconSpace: encodingSpaceType = field(
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    encodingLimits: encodingLimitsType = field(
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    trajectory: trajectoryType = field(
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    trajectoryDescription: None | trajectoryDescriptionType = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    parallelImaging: None | parallelImagingType = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )
    echoTrainLength: None | int = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        },
    )


@dataclass(kw_only=True)
class ismrmrdHeader:
    class Meta:
        namespace = "http://www.ismrm.org/ISMRMRD"

    version: None | int = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    subjectInformation: None | subjectInformationType = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    studyInformation: None | studyInformationType = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    measurementInformation: None | measurementInformationType = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    acquisitionSystemInformation: None | acquisitionSystemInformationType = (
        field(
            default=None,
            metadata={
                "type": "Element",
            },
        )
    )
    experimentalConditions: experimentalConditionsType = field(
        metadata={
            "type": "Element",
        }
    )
    encoding: list[encodingType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    sequenceParameters: None | sequenceParametersType = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    userParameters: None | userParametersType = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    waveformInformation: list[waveformInformationType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "max_occurs": 32,
        },
    )
