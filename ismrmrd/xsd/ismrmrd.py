from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import List, Optional

__NAMESPACE__ = "http://www.ismrm.org/ISMRMRD"


@dataclass
class accelerationFactorType:
    """
    :ivar kspace_encoding_step_1:
    :ivar kspace_encoding_step_2:
    """
    kspace_encoding_step_1: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
            "required": True,
        }
    )
    kspace_encoding_step_2: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
            "required": True,
        }
    )


class calibrationModeType(Enum):
    """
    :cvar EMBEDDED:
    :cvar INTERLEAVED:
    :cvar SEPARATE:
    :cvar EXTERNAL:
    :cvar OTHER:
    """
    EMBEDDED = "embedded"
    INTERLEAVED = "interleaved"
    SEPARATE = "separate"
    EXTERNAL = "external"
    OTHER = "other"


@dataclass
class coilLabelType:
    """
    :ivar coil_number:
    :ivar coil_name:
    """
    coil_number: Optional[int] = field(
        default=None,
        metadata={
            "name": "coilNumber",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
            "required": True,
        }
    )
    coil_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "coilName",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
            "required": True,
        }
    )


@dataclass
class experimentalConditionsType:
    """
    :ivar h1resonance_frequency_hz:
    """
    h1resonance_frequency_hz: Optional[int] = field(
        default=None,
        metadata={
            "name": "H1resonanceFrequency_Hz",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
            "required": True,
        }
    )


@dataclass
class fieldOfViewMm:
    """
    :ivar x:
    :ivar y:
    :ivar z:
    """
    class Meta:
        name = "fieldOfView_mm"

    x: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
            "required": True,
        }
    )
    y: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
            "required": True,
        }
    )
    z: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
            "required": True,
        }
    )


class interleavingDimensionType(Enum):
    """
    :cvar PHASE:
    :cvar REPETITION:
    :cvar CONTRAST:
    :cvar AVERAGE:
    :cvar OTHER:
    """
    PHASE = "phase"
    REPETITION = "repetition"
    CONTRAST = "contrast"
    AVERAGE = "average"
    OTHER = "other"


@dataclass
class limitType:
    """
    :ivar minimum:
    :ivar maximum:
    :ivar center:
    """
    minimum: int = field(
        default=0,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
            "required": True,
        }
    )
    maximum: int = field(
        default=0,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
            "required": True,
        }
    )
    center: int = field(
        default=0,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
            "required": True,
        }
    )


@dataclass
class matrixSize:
    """
    :ivar x:
    :ivar y:
    :ivar z:
    """
    x: int = field(
        default=1,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
            "required": True,
        }
    )
    y: int = field(
        default=1,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
            "required": True,
        }
    )
    z: int = field(
        default=1,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
            "required": True,
        }
    )


@dataclass
class measurementDependencyType:
    """
    :ivar dependency_type:
    :ivar measurement_id:
    """
    dependency_type: Optional[str] = field(
        default=None,
        metadata={
            "name": "dependencyType",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
            "required": True,
        }
    )
    measurement_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "measurementID",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
            "required": True,
        }
    )


@dataclass
class referencedImageSequence:
    """
    :ivar referenced_sopinstance_uid:
    """
    referenced_sopinstance_uid: List[str] = field(
        default_factory=list,
        metadata={
            "name": "referencedSOPInstanceUID",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )


@dataclass
class sequenceParametersType:
    """
    :ivar tr:
    :ivar te:
    :ivar ti:
    :ivar flip_angle_deg:
    :ivar sequence_type:
    :ivar echo_spacing:
    """
    tr: List[float] = field(
        default_factory=list,
        metadata={
            "name": "TR",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    te: List[float] = field(
        default_factory=list,
        metadata={
            "name": "TE",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    ti: List[float] = field(
        default_factory=list,
        metadata={
            "name": "TI",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    flip_angle_deg: List[float] = field(
        default_factory=list,
        metadata={
            "name": "flipAngle_deg",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    sequence_type: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    echo_spacing: List[float] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )


@dataclass
class studyInformationType:
    """
    :ivar study_date:
    :ivar study_time:
    :ivar study_id:
    :ivar accession_number:
    :ivar referring_physician_name:
    :ivar study_description:
    :ivar study_instance_uid:
    """
    study_date: Optional[str] = field(
        default=None,
        metadata={
            "name": "studyDate",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    study_time: Optional[str] = field(
        default=None,
        metadata={
            "name": "studyTime",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    study_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "studyID",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    accession_number: Optional[int] = field(
        default=None,
        metadata={
            "name": "accessionNumber",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    referring_physician_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "referringPhysicianName",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    study_description: Optional[str] = field(
        default=None,
        metadata={
            "name": "studyDescription",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    study_instance_uid: Optional[str] = field(
        default=None,
        metadata={
            "name": "studyInstanceUID",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )


@dataclass
class subjectInformationType:
    """
    :ivar patient_name:
    :ivar patient_weight_kg:
    :ivar patient_id:
    :ivar patient_birthdate:
    :ivar patient_gender:
    """
    patient_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "patientName",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    patient_weight_kg: Optional[float] = field(
        default=None,
        metadata={
            "name": "patientWeight_kg",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    patient_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "patientID",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    patient_birthdate: Optional[str] = field(
        default=None,
        metadata={
            "name": "patientBirthdate",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    patient_gender: Optional[str] = field(
        default=None,
        metadata={
            "name": "patientGender",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
            "pattern": r"[MFO]",
        }
    )


class trajectoryType(Enum):
    """
    :cvar CARTESIAN:
    :cvar EPI:
    :cvar RADIAL:
    :cvar GOLDENANGLE:
    :cvar SPIRAL:
    :cvar OTHER:
    """
    CARTESIAN = "cartesian"
    EPI = "epi"
    RADIAL = "radial"
    GOLDENANGLE = "goldenangle"
    SPIRAL = "spiral"
    OTHER = "other"


@dataclass
class userParameterBase64Type:
    """
    :ivar name:
    :ivar value:
    """
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
            "required": True,
        }
    )
    value: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
            "required": True,
        }
    )


@dataclass
class userParameterDoubleType:
    """
    :ivar name:
    :ivar value:
    """
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
            "required": True,
        }
    )
    value: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
            "required": True,
        }
    )


@dataclass
class userParameterLongType:
    """
    :ivar name:
    :ivar value:
    """
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
            "required": True,
        }
    )
    value: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
            "required": True,
        }
    )


@dataclass
class userParameterStringType:
    """
    :ivar name:
    :ivar value:
    """
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
            "required": True,
        }
    )
    value: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
            "required": True,
        }
    )


@dataclass
class acquisitionSystemInformationType:
    """
    :ivar system_vendor:
    :ivar system_model:
    :ivar system_field_strength_t:
    :ivar relative_receiver_noise_bandwidth:
    :ivar receiver_channels:
    :ivar coil_label:
    :ivar institution_name:
    :ivar station_name:
    """
    system_vendor: Optional[str] = field(
        default=None,
        metadata={
            "name": "systemVendor",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    system_model: Optional[str] = field(
        default=None,
        metadata={
            "name": "systemModel",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    system_field_strength_t: Optional[float] = field(
        default=None,
        metadata={
            "name": "systemFieldStrength_T",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    relative_receiver_noise_bandwidth: Optional[float] = field(
        default=None,
        metadata={
            "name": "relativeReceiverNoiseBandwidth",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    receiver_channels: Optional[int] = field(
        default=None,
        metadata={
            "name": "receiverChannels",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    coil_label: List[coilLabelType] = field(
        default_factory=list,
        metadata={
            "name": "coilLabel",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    institution_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "institutionName",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    station_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "stationName",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )


@dataclass
class encodingLimitsType:
    """
    :ivar kspace_encoding_step_0:
    :ivar kspace_encoding_step_1:
    :ivar kspace_encoding_step_2:
    :ivar average:
    :ivar slice:
    :ivar contrast:
    :ivar phase:
    :ivar repetition:
    :ivar set:
    :ivar segment:
    """
    kspace_encoding_step_0: Optional[limitType] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    kspace_encoding_step_1: Optional[limitType] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    kspace_encoding_step_2: Optional[limitType] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    average: Optional[limitType] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    slice: Optional[limitType] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    contrast: Optional[limitType] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    phase: Optional[limitType] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    repetition: Optional[limitType] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    set: Optional[limitType] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    segment: Optional[limitType] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )


@dataclass
class encodingSpaceType:
    """
    :ivar matrix_size:
    :ivar field_of_view_mm:
    """
    matrix_size: Optional[matrixSize] = field(
        default=None,
        metadata={
            "name": "matrixSize",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
            "required": True,
        }
    )
    field_of_view_mm: Optional[fieldOfViewMm] = field(
        default=None,
        metadata={
            "name": "fieldOfView_mm",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
            "required": True,
        }
    )


@dataclass
class measurementInformationType:
    """
    :ivar measurement_id:
    :ivar series_date:
    :ivar series_time:
    :ivar patient_position:
    :ivar initial_series_number:
    :ivar protocol_name:
    :ivar series_description:
    :ivar measurement_dependency:
    :ivar series_instance_uidroot:
    :ivar frame_of_reference_uid:
    :ivar referenced_image_sequence:
    """
    measurement_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "measurementID",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    series_date: Optional[str] = field(
        default=None,
        metadata={
            "name": "seriesDate",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    series_time: Optional[str] = field(
        default=None,
        metadata={
            "name": "seriesTime",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    patient_position: Optional["measurementInformationType.patientPosition"] = field(
        default=None,
        metadata={
            "name": "patientPosition",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
            "required": True,
        }
    )
    initial_series_number: Optional[int] = field(
        default=None,
        metadata={
            "name": "initialSeriesNumber",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    protocol_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "protocolName",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    series_description: Optional[str] = field(
        default=None,
        metadata={
            "name": "seriesDescription",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    measurement_dependency: List[measurementDependencyType] = field(
        default_factory=list,
        metadata={
            "name": "measurementDependency",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    series_instance_uidroot: Optional[str] = field(
        default=None,
        metadata={
            "name": "seriesInstanceUIDRoot",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    frame_of_reference_uid: Optional[str] = field(
        default=None,
        metadata={
            "name": "frameOfReferenceUID",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    referenced_image_sequence: Optional[referencedImageSequence] = field(
        default=None,
        metadata={
            "name": "referencedImageSequence",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )

    class patientPosition(Enum):
        """
        :cvar HFP:
        :cvar HFS:
        :cvar HFDR:
        :cvar HFDL:
        :cvar FFP:
        :cvar FFS:
        :cvar FFDR:
        :cvar FFDL:
        """
        HFP = "HFP"
        HFS = "HFS"
        HFDR = "HFDR"
        HFDL = "HFDL"
        FFP = "FFP"
        FFS = "FFS"
        FFDR = "FFDR"
        FFDL = "FFDL"


@dataclass
class parallelImagingType:
    """
    :ivar acceleration_factor:
    :ivar calibration_mode:
    :ivar interleaving_dimension:
    """
    acceleration_factor: Optional[accelerationFactorType] = field(
        default=None,
        metadata={
            "name": "accelerationFactor",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
            "required": True,
        }
    )
    calibration_mode: Optional[calibrationModeType] = field(
        default=None,
        metadata={
            "name": "calibrationMode",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    interleaving_dimension: Optional[interleavingDimensionType] = field(
        default=None,
        metadata={
            "name": "interleavingDimension",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )


@dataclass
class trajectoryDescriptionType:
    """
    :ivar identifier:
    :ivar user_parameter_long:
    :ivar user_parameter_double:
    :ivar comment:
    """
    identifier: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
            "required": True,
        }
    )
    user_parameter_long: List[userParameterLongType] = field(
        default_factory=list,
        metadata={
            "name": "userParameterLong",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    user_parameter_double: List[userParameterDoubleType] = field(
        default_factory=list,
        metadata={
            "name": "userParameterDouble",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    comment: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )


@dataclass
class userParameters:
    """
    :ivar user_parameter_long:
    :ivar user_parameter_double:
    :ivar user_parameter_string:
    :ivar user_parameter_base64:
    """
    user_parameter_long: List[userParameterLongType] = field(
        default_factory=list,
        metadata={
            "name": "userParameterLong",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    user_parameter_double: List[userParameterDoubleType] = field(
        default_factory=list,
        metadata={
            "name": "userParameterDouble",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    user_parameter_string: List[userParameterStringType] = field(
        default_factory=list,
        metadata={
            "name": "userParameterString",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    user_parameter_base64: List[userParameterBase64Type] = field(
        default_factory=list,
        metadata={
            "name": "userParameterBase64",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )


@dataclass
class encodingType:
    """
    :ivar encoded_space:
    :ivar recon_space:
    :ivar encoding_limits:
    :ivar trajectory:
    :ivar trajectory_description:
    :ivar parallel_imaging:
    :ivar echo_train_length:
    """
    encoded_space: Optional[encodingSpaceType] = field(
        default=None,
        metadata={
            "name": "encodedSpace",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
            "required": True,
        }
    )
    recon_space: Optional[encodingSpaceType] = field(
        default=None,
        metadata={
            "name": "reconSpace",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
            "required": True,
        }
    )
    encoding_limits: Optional[encodingLimitsType] = field(
        default=None,
        metadata={
            "name": "encodingLimits",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
            "required": True,
        }
    )
    trajectory: Optional[trajectoryType] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
            "required": True,
        }
    )
    trajectory_description: Optional[trajectoryDescriptionType] = field(
        default=None,
        metadata={
            "name": "trajectoryDescription",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    parallel_imaging: Optional[parallelImagingType] = field(
        default=None,
        metadata={
            "name": "parallelImaging",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )
    echo_train_length: Optional[int] = field(
        default=None,
        metadata={
            "name": "echoTrainLength",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
        }
    )


@dataclass
class waveformInformation:
    """
    :ivar waveform_name:
    :ivar waveform_type:
    :ivar user_parameters:
    """
    waveform_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "waveformName",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
            "required": True,
        }
    )
    waveform_type: Optional["waveformInformation.waveformType"] = field(
        default=None,
        metadata={
            "name": "waveformType",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
            "required": True,
        }
    )
    user_parameters: Optional[userParameters] = field(
        default=None,
        metadata={
            "name": "userParameters",
            "type": "Element",
            "namespace": "http://www.ismrm.org/ISMRMRD",
            "required": True,
        }
    )

    class waveformType(Enum):
        """
        :cvar ECG:
        :cvar PULSE:
        :cvar RESPIRATORY:
        :cvar TRIGGER:
        :cvar GRADIENTWAVEFORM:
        :cvar OTHER:
        """
        ECG = "ecg"
        PULSE = "pulse"
        RESPIRATORY = "respiratory"
        TRIGGER = "trigger"
        GRADIENTWAVEFORM = "gradientwaveform"
        OTHER = "other"


@dataclass
class ismrmrdHeader:
    """
    :ivar version:
    :ivar subject_information:
    :ivar study_information:
    :ivar measurement_information:
    :ivar acquisition_system_information:
    :ivar experimental_conditions:
    :ivar encoding:
    :ivar sequence_parameters:
    :ivar user_parameters:
    :ivar waveform_information:
    """
    class Meta:
        namespace = "http://www.ismrm.org/ISMRMRD"

    version: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
        }
    )
    subject_information: Optional[subjectInformationType] = field(
        default=None,
        metadata={
            "name": "subjectInformation",
            "type": "Element",
        }
    )
    study_information: Optional[studyInformationType] = field(
        default=None,
        metadata={
            "name": "studyInformation",
            "type": "Element",
        }
    )
    measurement_information: Optional[measurementInformationType] = field(
        default=None,
        metadata={
            "name": "measurementInformation",
            "type": "Element",
        }
    )
    acquisition_system_information: Optional[acquisitionSystemInformationType] = field(
        default=None,
        metadata={
            "name": "acquisitionSystemInformation",
            "type": "Element",
        }
    )
    experimental_conditions: Optional[experimentalConditionsType] = field(
        default=None,
        metadata={
            "name": "experimentalConditions",
            "type": "Element",
            "required": True,
        }
    )
    encoding: List[encodingType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        }
    )
    sequence_parameters: Optional[sequenceParametersType] = field(
        default=None,
        metadata={
            "name": "sequenceParameters",
            "type": "Element",
        }
    )
    user_parameters: Optional[userParameters] = field(
        default=None,
        metadata={
            "name": "userParameters",
            "type": "Element",
        }
    )
    waveform_information: List[waveformInformation] = field(
        default_factory=list,
        metadata={
            "name": "waveformInformation",
            "type": "Element",
            "max_occurs": 32,
        }
    )
