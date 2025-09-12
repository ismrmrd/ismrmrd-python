import ismrmrd
import shutil
import os.path
import tempfile
import numpy
import pytest
from test_common import *

@pytest.fixture(autouse=True)
def temp_dir_fixture():
    global temp_dir
    temp_dir = tempfile.mkdtemp(prefix='ismrmrd-python-', suffix='-test')
    yield
    shutil.rmtree(temp_dir, ignore_errors=True)

def random_acquisitions(n):
    yield from (create_random_acquisition(i) for i in range(n))

def random_waveforms(n):
    yield from (create_random_waveform(i) for i in range(n))

def random_images(n):
    yield from (create_random_image(i) for i in range(n))

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
        assert not (dataset.acquisitions is None)

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

def test_file_can_delete_acquisitions():
    filename = os.path.join(temp_dir, "acquisitions.h5")
    with ismrmrd.File(filename) as file:
        dataset = file['dataset']
        assert dataset.acquisitions is None
        del dataset.acquisitions
        assert dataset.acquisitions is None
        dataset.acquisitions = random_acquisitions(10)
        assert not (dataset.acquisitions is None)
        del dataset.acquisitions
        assert dataset.acquisitions is None

def test_file_can_access_random_acquisition():
    filename = os.path.join(temp_dir, "acquisitions.h5")
    acquisitions = list(random_acquisitions(256))
    with ismrmrd.File(filename) as file:
        dataset = file['dataset']
        dataset.acquisitions = acquisitions
    with ismrmrd.File(filename) as file:
        dataset = file['dataset']
        assert acquisitions[255] == dataset.acquisitions[255]

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

def test_file_can_append_acquisitions():
    filename = os.path.join(temp_dir, "acquisitions.h5")
    acquisitions = list(random_acquisitions(10))
    acquisitions2 = list(random_acquisitions(10))
    acquisition3 = next(random_acquisitions(1))
    combined = acquisitions + acquisitions2 + [acquisition3]
    with ismrmrd.File(filename) as file:
        dataset = file['dataset']
        dataset.acquisitions = acquisitions
        dataset.acquisitions.extend(acquisitions2)
        dataset.acquisitions.append(acquisition3)
    with ismrmrd.File(filename) as file:
        dataset = file['dataset']
        for a, b in zip(combined, dataset.acquisitions):
            assert a == b

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

def test_file_cannot_write_mismatched_slice():
    filename = os.path.join(temp_dir, "acquisitions.h5")
    acquisitions = list(random_acquisitions(256))
    slice = list(random_acquisitions(3))
    with pytest.raises(TypeError):
        with ismrmrd.File(filename) as file:
            dataset = file['dataset']
            dataset.acquisitions = acquisitions
            dataset.acquisitions[150:155] = slice

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

def test_file_can_append_waveforms():
    filename = os.path.join(temp_dir, "waveforms.h5")
    waveforms = list(random_waveforms(10))
    waveforms2 = list(random_waveforms(10))
    waveform3 = next(random_waveforms(1))
    combined = waveforms + waveforms2 + [waveform3]
    with ismrmrd.File(filename) as file:
        dataset = file['dataset']
        dataset.waveforms = waveforms
        dataset.waveforms.extend(waveforms2)
        dataset.waveforms.append(waveform3)
    with ismrmrd.File(filename) as file:
        dataset = file['dataset']
        for a, b in zip(combined, dataset.waveforms):
            assert a == b

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

def test_file_can_read_random_image():
    filename = os.path.join(temp_dir, "images.h5")
    images = list(random_images(10))
    with ismrmrd.File(filename) as file:
        imageset = file['dataset/image_1']
        imageset.images = images
    with ismrmrd.File(filename) as file:
        imageset = file['dataset/image_1']
        assert images[8] == imageset.images[8]

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

def test_file_can_list_keys():
    filename = os.path.join(temp_dir, "keys.h5")
    with ismrmrd.File(filename) as file:
        dataset = file['dataset']
        dataset.acquisitions = random_acquisitions(10)
        dataset2 = file['dataset2']
        dataset2.acquisitions = random_acquisitions(10)
    with ismrmrd.File(filename) as file:
        assert(file.keys() == {'dataset', 'dataset2' })

def test_file_cannot_write_image_on_data():
    filename = os.path.join(temp_dir, "file.h5")
    with ismrmrd.File(filename) as file:
        dataset = file['dataset']
        dataset.acquisitions = random_acquisitions(10)
    with pytest.raises(TypeError):
        with ismrmrd.File(filename) as file:
            dataset = file['dataset']
            dataset.images = random_images(1)

def test_file_cannot_write_data_on_image():
    filename = os.path.join(temp_dir, "file.h5")
    with ismrmrd.File(filename) as file:
        dataset = file['dataset']
        dataset.images = random_images(1)
    with pytest.raises(TypeError):
        with ismrmrd.File(filename) as file:
            dataset = file['dataset']
            dataset.acquisitions = random_acquisitions(10)

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

def test_file_can_read_and_write_headers():
    filename = os.path.join(temp_dir, "file.h5")
    header = create_example_ismrmrd_header()
    with ismrmrd.File(filename) as file:
        dataset = file['dataset']
        dataset.header = header
    with ismrmrd.File(filename) as file:
        dataset = file['dataset']
        assert ismrmrd.xsd.ToXML(header) == ismrmrd.xsd.ToXML(dataset.header)
        assert header == dataset.header
