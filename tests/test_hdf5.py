import ismrmrd
import pytest

import random
import numpy.random

import shutil
import os.path
import ctypes

import tempfile

from test_common import *


@pytest.fixture(autouse=True)
def temp_dir_fixture():
    global temp_dir
    temp_dir = tempfile.mkdtemp(prefix='ismrmrd-python-', suffix='-test')
    yield
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_open_fresh_hdf5():
    filename = os.path.join(temp_dir, 'open_fresh.h5')
    ismrmrd.Dataset(filename)


def test_hdf5_fileinfo():
    filename = os.path.join(temp_dir, 'stuff.h5')

    dataset = ismrmrd.Dataset(filename, 'dataset')
    dataset.append_acquisition(create_random_acquisition())

    other_dataset = ismrmrd.Dataset(filename, 'other_dataset')
    other_dataset.append_acquisition(create_random_acquisition())

    assert ismrmrd.hdf5.fileinfo(filename) == ['dataset', 'other_dataset']


def test_read_and_write_acquisitions_to_hdf5():
    filename = os.path.join(temp_dir, 'read_write_acquisitions.h5')

    acquisitions = [create_random_acquisition(seed) for seed in range(0, 128)]

    dataset = ismrmrd.Dataset(filename)
    for acquisition in acquisitions:
        dataset.append_acquisition(acquisition)
    dataset.close()

    dataset = ismrmrd.Dataset(filename)
    nacquisitions = dataset.number_of_acquisitions()
    assert nacquisitions == len(acquisitions), \
        "Number of acquisitions in written file does not match the number appended."

    read_acquisitions = [dataset.read_acquisition(i) for i in range(0, nacquisitions)]

    for acq_a, acq_b in zip(acquisitions, read_acquisitions):
        compare_acquisitions(acq_a, acq_b)


def test_read_and_write_images_to_hdf5():
    filename = os.path.join(temp_dir, 'read_write_images.h5')

    images = [create_random_image(seed) for seed in range(0, 16)]

    dataset = ismrmrd.Dataset(filename)
    for image in images:
        dataset.append_image('images', image)
    dataset.close()

    dataset = ismrmrd.Dataset(filename)
    nimages = dataset.number_of_images('images')
    assert nimages == len(images), \
        "Number of images in written file does not match the number appended."

    read_images = [dataset.read_image('images', i) for i in range(0, nimages)]

    for img_a, img_b in zip(images, read_images):
        compare_images(img_a, img_b)


def test_read_and_write_waveforms_to_hdf5():
    filename = os.path.join(temp_dir, 'read_write_waveforms.h5')

    waveforms = [create_random_waveform(seed) for seed in range(0, 128)]

    dataset = ismrmrd.Dataset(filename)
    for waveform in waveforms:
        dataset.append_waveform(waveform)
    dataset.close()

    dataset = ismrmrd.Dataset(filename)
    nwaveforms = dataset.number_of_waveforms()
    assert nwaveforms == len(waveforms), \
        "Number of waveforms in written file does not match the number appended."

    read_waveforms = [dataset.read_waveform(i) for i in range(0, nwaveforms)]

    for wav_a, wav_b in zip(waveforms, read_waveforms):
        compare_waveforms(wav_a, wav_b)


def test_waveform_hdf5_size():
    assert ismrmrd.hdf5.waveform_header_dtype.itemsize == 40
