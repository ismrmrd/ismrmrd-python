import os
import argparse
import numpy as np
from pathlib import Path

import ismrmrd

def test_basic_recon(reference_file, testdata_file):
    reference_reader = ismrmrd.ProtocolDeserializer(reference_file)
    reference_images = list(reference_reader.deserialize())

    testdata_reader = ismrmrd.ProtocolDeserializer(testdata_file)
    test_stream = list(testdata_reader.deserialize())
    # The reconstruction may or may not include the ismrmrdHeader
    if len(test_stream) > 1:
        assert len(test_stream) == 2
        test_header = test_stream[0]
        assert isinstance(test_header, ismrmrd.xsd.ismrmrdHeader), "First object in test stream should be an IsmrmrdHeader"
        test_images = test_stream[1:]
    else:
        test_images = test_stream

    assert len(test_images) == len(reference_images), "Expected matching number of reference and test images"
    for ref_img, test_img in zip(reference_images, test_images):
        ref_norm = normalize(ref_img.data)
        test_norm = normalize(test_img.data)
        assert np.allclose(ref_norm, test_norm), "Normalized reference and test images do not match closely enough"

        # assert test_img.version == ref_img.version
        assert test_img.measurement_uid == ref_img.measurement_uid
        assert test_img.position[:] == ref_img.position[:]
        assert test_img.read_dir[:] == ref_img.read_dir[:]
        assert test_img.phase_dir[:] == ref_img.phase_dir[:]
        assert test_img.slice_dir[:] == ref_img.slice_dir[:]
        assert test_img.patient_table_position[:] == ref_img.patient_table_position[:]
        assert test_img.acquisition_time_stamp == ref_img.acquisition_time_stamp
        assert test_img.physiology_time_stamp[:] == ref_img.physiology_time_stamp[:]
        assert test_img.image_type == ref_img.image_type
        assert test_img.image_index == ref_img.image_index
        assert test_img.image_series_index == ref_img.image_series_index
        assert test_img.user_int[:] == ref_img.user_int[:]
        assert test_img.user_float[:] == ref_img.user_float[:]


# Z-score normalization function
def normalize(data):
    return (data - np.mean(data)) / np.std(data)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Validate results of a streaming ismrmrd reconstruction')
    parser.add_argument('--reference', type=str, help='Reference image stream', required=True)
    parser.add_argument('--testdata', type=str, help='Test image stream', required=True)
    args = parser.parse_args()
    with open(args.testdata, 'rb') as testdata_file:
        with open(args.reference, 'rb') as reference_file:
            test_basic_recon(reference_file, testdata_file)
