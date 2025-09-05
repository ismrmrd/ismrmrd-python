import os
import argparse
import numpy as np
from pathlib import Path

import ismrmrd

def test_basic_recon(reference_filename, testdata_file):
    reference_reader = ismrmrd.ProtocolDeserializer(reference_file)
    reference_images = list(reference_reader.deserialize())

    testdata_reader = ismrmrd.ProtocolDeserializer(testdata_file)
    test_images = list(testdata_reader.deserialize())
    assert len(test_images) == len(reference_images), "Expected matching number of reference and test images"

    for ref_img, test_img in zip(reference_images, test_images):
        assert np.allclose(ref_img.data, test_img.data)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Validate results of a streaming ismrmrd reconstruction')
    parser.add_argument('--reference', type=str, help='Reference image stream', required=True)
    parser.add_argument('--testdata', type=str, help='Test image stream', required=True)
    args = parser.parse_args()
    with open(args.testdata, 'rb') as testdata_file:
        with open(args.reference, 'rb') as reference_file:
            test_basic_recon(reference_file, testdata_file)
