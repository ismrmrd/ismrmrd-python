

import ismrmrd


import nose.tools

import random
import numpy.random

import shutil
import os.path
import ctypes

import tempfile

from test_common import *


temp_dir = None


def create_temp_dir():
    global temp_dir
    temp_dir = tempfile.mkdtemp(prefix='ismrmrd-python-', suffix='-test')


def delete_temp_dir():
    shutil.rmtree(temp_dir, ignore_errors=True)


@nose.tools.with_setup(create_temp_dir, delete_temp_dir)
def test_open_fresh_hdf5():
    filename = os.path.join(temp_dir, 'open_fresh.h5')
    ismrmrd.Dataset(filename)


@nose.tools.with_setup(create_temp_dir, delete_temp_dir)
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

    map(lambda acq_a, acq_b: compare_acquisitions(acq_a, acq_b), acquisitions, read_acquisitions)


@nose.tools.with_setup(create_temp_dir, delete_temp_dir)
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

    map(lambda img_a, img_b: compare_images(img_a, img_b), images, read_images)


@nose.tools.with_setup(create_temp_dir, delete_temp_dir)
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

    map(lambda wav_a, wav_b: compare_waveforms(wav_a, wav_b), waveforms, read_waveforms)

def test_waveform_hdf5_size():
    assert ismrmrd.hdf5.waveform_header_dtype.itemsize == 40
