
import h5py
import numpy

from .hdf5 import *
from .acquisition import *
from .waveform import *
from .image import *


class Container:

    def __init__(self, contents):
        self.__contents = contents

    def __getitem__(self, key):
        if key in self.__contents:
            return Container(self.__contents[key])
        return self.__missing__(key)

    def __setitem__(self, key, value):
        raise NotImplementedError("Setting items is not well defined. Please refrain from doing so.")

    def __delitem__(self, key):
        del self.__contents[key]

    def __missing__(self, key):
        return Container(self.__contents.require_group(key))

    def __contains__(self, key):
        return key in self.__contents

    def __iter__(self):
        for key in self.__contents:
            if isinstance(self.__contents[key], h5py.Group):
                yield key

    def __str__(self):
        return str([key for key, item in self.__contents.items()])

    def __get_acquisitions(self):
        data = self.__contents.get('data', [])

        for raw in data:
            acquisition = Acquisition(raw['head'])

            acquisition.data[:] = raw['data'].view(np.complex64).reshape(
                (acquisition.active_channels,
                 acquisition.number_of_samples)
            )[:]

            acquisition.traj[:] = raw['traj'].reshape(
                (acquisition.number_of_samples,
                 acquisition.trajectory_dimensions)
            )[:]

            yield acquisition

    def __set_acquisitions(self, acquisitions):

        def as_numpy_structure(acq):
            return (
                np.frombuffer(acq.getHead(), dtype=acquisition_header_dtype),
                acq.traj.view(np.float32).reshape((acq.number_of_samples * acq.trajectory_dimensions,)),
                acq.data.view(np.float32).reshape((2 * acq.active_channels * acq.number_of_samples,))
            )

        buffer = numpy.array([as_numpy_structure(a) for a in acquisitions], dtype=acquisition_dtype)

        self.__del_acquisitions()
        self.__contents['data'] = buffer

    def __del_acquisitions(self):
        if 'data' in self.__contents:
            del self.__contents['data']

    acquisitions = property(__get_acquisitions, __set_acquisitions, __del_acquisitions)

    def __get_waveforms(self):
        data = self.__contents.get('waveforms', [])

        for raw in data:
            # Notice the array. Lovely.
            waveform = Waveform(numpy.array(raw['head'], dtype=waveform_header_dtype))
            waveform.data[:] = raw['data'].view(np.uint32).reshape(
                (waveform.channels,
                 waveform.number_of_samples)
            )[:]

            yield waveform

    def __set_waveforms(self, waveforms):

        def as_numpy_structure(wav):
            return (
                np.frombuffer(wav.getHead(), dtype=waveform_header_dtype),
                wav.data.view(np.uint32).reshape((wav.channels * wav.number_of_samples,))
            )

        buffer = numpy.array([as_numpy_structure(w) for w in waveforms], dtype=waveform_dtype)

        self.__del_waveforms()
        self.__contents['waveforms'] = buffer

    def __del_waveforms(self):
        if 'waveforms' in self.__contents:
            del self.__contents['waveforms']

    waveforms = property(__get_waveforms, __set_waveforms, __del_waveforms)

    def __get_images(self):
        data = self.__contents.get('data', [])
        headers = self.__contents.get('headers', [])
        attributes = self.__contents.get('attributes', [])

        for data, header, attribute in zip(data, headers, attributes):
            image = Image(header, attribute)
            image.data[:] = data
            yield image

    def __set_images(self, images):

        images = list(images)

        data = numpy.stack([image.data for image in images])
        headers = numpy.stack([np.frombuffer(image.getHead(), dtype=image_header_dtype) for image in images])
        attributes = numpy.stack([image.attribute_string for image in images])

        self.__del_images()
        self.__contents.create_dataset('data', data=data)
        self.__contents.create_dataset('headers', data=headers)
        self.__contents.create_dataset('attributes', shape=attributes.shape, dtype=h5py.special_dtype(vlen=str))
        self.__contents['attributes'][:] = attributes

    def __del_images(self):
        for key in ['headers', 'data', 'attributes']:
            if key in self.__contents:
                del self.__contents[key]

    images = property(__get_images, __set_images, __del_images)

    def has_images(self):
        return all((key in self.__contents for key in ['data', 'headers', 'attributes']))

    def has_waveforms(self):
        return 'waveforms' in self.__contents

    def has_acquisitions(self):
        return 'data' in self.__contents and not self.has_images()

    arrays = property()

    def __visit(self, callback, path):

        callback(self, path)

        for key in self:
            child = self[key]
            child.__visit(callback, path + '/' + key)

    def visit(self, callback):
        for key in self:
            child = self[key]
            child.__visit(callback, key)

    def find_images(self):

        images = set()

        def find_images(node, path):
            if node.has_images():
                images.add(path)

        self.visit(find_images)
        return images

    def find_data(self):

        data = set()

        def find_data(node, path):
            if node.has_acquisitions() or node.has_waveforms():
                data.add(path)

        self.visit(find_data)
        return data


class File(Container):

    def __init__(self, filename, mode='a'):
        self.__file = h5py.File(filename, mode)
        super().__init__(self.__file)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.__file.close()
