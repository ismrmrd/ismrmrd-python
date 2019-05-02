import ismrmrd

import nose.tools

import shutil
import os.path
import tempfile

import numpy

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
def test_file_returns_none_when_no_acquisitions_present():

    filename = os.path.join(temp_dir, "acquisitions.h5")
    acquisitions = list(random_acquisitions(10))

    with ismrmrd.File(filename) as file:
        dataset = file['dataset']

        assert not dataset.has_acquisitions()
        assert dataset.acquisitions is None

        dataset.acquisitions = acquisitions

    with ismrmrd.File(filename) as file:
        dataset = file['dataset']

        assert dataset.has_acquisitions()
        assert dataset.acquisitions is not None


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
            assert a == b


@nose.tools.with_setup(create_temp_dir, delete_temp_dir)
def test_file_can_delete_acquisitions():

    filename = os.path.join(temp_dir, "acquisitions.h5")

    with ismrmrd.File(filename) as file:
        dataset = file['dataset']

        assert dataset.acquisitions is None
        del dataset.acquisitions
        assert dataset.acquisitions is None

        dataset.acquisitions = random_acquisitions(10)

        assert dataset.acquisitions is not None
        del dataset.acquisitions
        assert dataset.acquisitions is None


@nose.tools.with_setup(create_temp_dir, delete_temp_dir)
def test_file_can_access_random_acquisition():

    filename = os.path.join(temp_dir, "acquisitions.h5")
    acquisitions = list(random_acquisitions(256))

    with ismrmrd.File(filename) as file:
        dataset = file['dataset']
        dataset.acquisitions = acquisitions

    with ismrmrd.File(filename) as file:
        dataset = file['dataset']
        assert acquisitions[255] == dataset.acquisitions[255]


@nose.tools.with_setup(create_temp_dir, delete_temp_dir)
def test_file_can_access_random_acquisition_slice():

    filename = os.path.join(temp_dir, "acquisitions.h5")
    acquisitions = list(random_acquisitions(256))

    with ismrmrd.File(filename) as file:
        dataset = file['dataset']
        dataset.acquisitions = acquisitions

    with ismrmrd.File(filename) as file:
        dataset = file['dataset']

        for a, b in zip(acquisitions[250:255], dataset.acquisitions[250:255]):
            assert a == b


@nose.tools.with_setup(create_temp_dir, delete_temp_dir)
def test_file_can_write_random_acquisition():

    filename = os.path.join(temp_dir, "acquisitions.h5")
    acquisitions = list(random_acquisitions(256))
    acquisition = create_random_acquisition()

    with ismrmrd.File(filename) as file:
        dataset = file['dataset']
        dataset.acquisitions = acquisitions
        dataset.acquisitions[200] = acquisition

    with ismrmrd.File(filename) as file:
        dataset = file['dataset']
        assert acquisition == dataset.acquisitions[200]


@nose.tools.with_setup(create_temp_dir, delete_temp_dir)
def test_file_can_write_random_acquisition_slice():

    filename = os.path.join(temp_dir, "acquisitions.h5")
    acquisitions = list(random_acquisitions(256))
    slice = list(random_acquisitions(3))

    with ismrmrd.File(filename) as file:
        dataset = file['dataset']
        dataset.acquisitions = acquisitions
        dataset.acquisitions[150:153] = slice

    with ismrmrd.File(filename) as file:
        dataset = file['dataset']

        for a, b in zip(slice, dataset.acquisitions[150:153]):
            assert a == b


@nose.tools.raises(TypeError)
@nose.tools.with_setup(create_temp_dir, delete_temp_dir)
def test_file_cannot_write_mismatched_slice():

    filename = os.path.join(temp_dir, "acquisitions.h5")
    acquisitions = list(random_acquisitions(256))
    slice = list(random_acquisitions(3))

    with ismrmrd.File(filename) as file:
        dataset = file['dataset']
        dataset.acquisitions = acquisitions
        dataset.acquisitions[150:155] = slice


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
            assert a == b


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
            assert a == b


@nose.tools.with_setup(create_temp_dir, delete_temp_dir)
def test_file_can_read_random_image():

    filename = os.path.join(temp_dir, "images.h5")
    images = list(random_images(10))

    with ismrmrd.File(filename) as file:
        imageset = file['dataset/image_1']
        imageset.images = images

    with ismrmrd.File(filename) as file:
        imageset = file['dataset/image_1']

        assert images[8] == imageset.images[8]


@nose.tools.with_setup(create_temp_dir, delete_temp_dir)
def test_file_can_write_random_image():

    filename = os.path.join(temp_dir, "images.h5")
    image = create_random_image()

    with ismrmrd.File(filename) as file:
        imageset = file['dataset/image_1']
        imageset.images = random_images(10)
        imageset.images[6] = image

    with ismrmrd.File(filename) as file:
        imageset = file['dataset/image_1']

        assert image == imageset.images[6]


@nose.tools.with_setup(create_temp_dir, delete_temp_dir)
def test_file_can_read_image_slice():

    filename = os.path.join(temp_dir, "images.h5")
    images = list(random_images(10))

    with ismrmrd.File(filename) as file:
        imageset = file['dataset/image_1']
        imageset.images = images

    with ismrmrd.File(filename) as file:
        imageset = file['dataset/image_1']
        for a, b in zip(images[5:10], imageset.images[5:10]):
            assert a == b


@nose.tools.with_setup(create_temp_dir, delete_temp_dir)
def test_file_can_write_image_slice():

    filename = os.path.join(temp_dir, "images.h5")
    images = list(random_images(10))

    with ismrmrd.File(filename) as file:
        imageset = file['dataset/image_1']
        imageset.images = random_images(32)
        imageset.images[5:15] = images

    with ismrmrd.File(filename) as file:
        imageset = file['dataset/image_1']

        for a, b in zip(images, imageset.images[5:15]):
            assert a == b


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


@nose.tools.raises(TypeError)
@nose.tools.with_setup(create_temp_dir, delete_temp_dir)
def test_file_cannot_write_image_on_data():

    filename = os.path.join(temp_dir, "file.h5")

    with ismrmrd.File(filename) as file:
        dataset = file['dataset']
        dataset.acquisitions = random_acquisitions(10)

    with ismrmrd.File(filename) as file:
        dataset = file['dataset']
        dataset.images = random_images(1)


@nose.tools.raises(TypeError)
@nose.tools.with_setup(create_temp_dir, delete_temp_dir)
def test_file_cannot_write_data_on_image():

    filename = os.path.join(temp_dir, "file.h5")

    with ismrmrd.File(filename) as file:
        dataset = file['dataset']
        dataset.images = random_images(1)

    with ismrmrd.File(filename) as file:
        dataset = file['dataset']
        dataset.acquisitions = random_acquisitions(10)


@nose.tools.with_setup(create_temp_dir, delete_temp_dir)
def test_file_can_rewrite_data_and_images():

    filename = os.path.join(temp_dir, "file.h5")

    with ismrmrd.File(filename) as file:
        dataset = file['dataset']
        dataset.acquisitions = random_acquisitions(20)
        dataset.acquisitions = random_acquisitions(10)
        dataset.waveforms = random_waveforms(10)
        dataset.waveforms = random_waveforms(5)
        dataset.acquisitions = random_acquisitions(5)

    with ismrmrd.File(filename) as file:
        imageset = file['dataset/images']
        imageset.images = random_images(1)
        imageset.images = random_images(2)
        imageset.images = random_images(3)


example_header = """<?xml version="1.0" encoding="utf-8"?>
<ismrmrdHeader xmlns="http://www.ismrm.org/ISMRMRD" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.ismrm.org/ISMRMRD ismrmrd.xsd">
   <experimentalConditions>
      <H1resonanceFrequency_Hz>32130323</H1resonanceFrequency_Hz>
   </experimentalConditions>
   <encoding>
      <encodedSpace>
         <matrixSize>
            <x>64</x>
            <y>64</y>
            <z>1</z>
         </matrixSize>
         <fieldOfView_mm>
            <x>300</x>
            <y>300</y>
            <z>40</z>
         </fieldOfView_mm>
      </encodedSpace>
      <reconSpace>
         <matrixSize>
            <x>64</x>
            <y>64</y>
            <z>1</z>
         </matrixSize>
         <fieldOfView_mm>
            <x>300</x>
            <y>300</y>
            <z>40</z>
         </fieldOfView_mm>
      </reconSpace>
      <trajectory>radial</trajectory>
      <encodingLimits>
      </encodingLimits>
   </encoding>
</ismrmrdHeader>
"""


@nose.tools.with_setup(create_temp_dir, delete_temp_dir)
def test_file_can_read_and_write_headers():

    filename = os.path.join(temp_dir, "file.h5")
    header = ismrmrd.xsd.CreateFromDocument(example_header)

    with ismrmrd.File(filename) as file:
        dataset = file['dataset']
        dataset.header = header

    with ismrmrd.File(filename) as file:
        dataset = file['dataset']
        assert header.toxml() == dataset.header.toxml()
