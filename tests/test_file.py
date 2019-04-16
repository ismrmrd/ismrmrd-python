import ismrmrd

import nose.tools

import shutil
import os.path

import tempfile

from test_common import *

temp_dir = None


def create_temp_dir():
    global temp_dir
    temp_dir = tempfile.mkdtemp(prefix='ismrmrd-python-', suffix='-test')


def delete_temp_dir():
    shutil.rmtree(temp_dir, ignore_errors=True)


def random_acquisitions(n):
    yield from (create_random_acquisition(i) for i in range(n))


def random_waveforms(n):
    yield from (create_random_waveform(i) for i in range(n))


def random_images(n):
    yield from (create_random_image(i) for i in range(n))


@nose.tools.with_setup(create_temp_dir, delete_temp_dir)
def test_file_can_read_and_write_acquisitions():

    filename = os.path.join(temp_dir, "acquisitions.h5")
    acquisitions = list(random_acquisitions(10))

    with ismrmrd.File(filename) as file:
        dataset = file['dataset']
        dataset.acquisitions = acquisitions

    with ismrmrd.File(filename) as file:
        dataset = file['dataset']
        for a, b in zip(acquisitions, dataset.acquisitions):
            compare_acquisitions(a, b)


@nose.tools.with_setup(create_temp_dir, delete_temp_dir)
def test_file_can_read_and_write_waveforms():

    filename = os.path.join(temp_dir, "waveforms.h5")
    waveforms = list(random_waveforms(10))

    with ismrmrd.File(filename) as file:
        dataset = file['dataset']
        dataset.waveforms = waveforms

    with ismrmrd.File(filename) as file:
        dataset = file['dataset']
        for a, b in zip(waveforms, dataset.waveforms):
            compare_waveforms(a, b)


@nose.tools.with_setup(create_temp_dir, delete_temp_dir)
def test_file_can_read_and_write_images():

    filename = os.path.join(temp_dir, "images.h5")
    images = list(random_images(10))

    with ismrmrd.File(filename) as file:
        imageset = file['dataset/image_1']
        imageset.images = images

    with ismrmrd.File(filename) as file:
        imageset = file['dataset/image_1']
        for a, b in zip(images, imageset.images):
            compare_images(a, b)


@nose.tools.with_setup(create_temp_dir, delete_temp_dir)
def test_file_can_list_contained_images():

    filename = os.path.join(temp_dir, "find_file.h5")

    with ismrmrd.File(filename) as file:
        dataset = file['dataset']
        dataset.acquisitions = random_acquisitions(10)

        imageset = file['dataset/image_1']
        imageset.images = random_images(1)

        imageset = file['dataset/image_2']
        imageset.images = random_images(2)

        imageset = file['dataset/nested/image_3']
        imageset.images = [create_random_image(3)]

    with ismrmrd.File(filename) as file:
        assert(file.find_images() == {'dataset/image_1', 'dataset/image_2', 'dataset/nested/image_3'})
        assert(file.find_data() == {'dataset'})



