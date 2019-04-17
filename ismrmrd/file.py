
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

    def __delitem__(self, key):
        if key in self.__contents:
            del self.__contents[key]

    def __missing__(self, key):
        return Container(self.__contents.require_group(key))

    def __contains__(self, key):
        return key in self.__contents

    def __iter__(self):
        for key, item in self.__contents.items():
            if isinstance(item, h5py.Group):
                yield key

    def __str__(self):
        return str([key for key in self.__contents])

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

        if self.has_images():
            raise TypeError("Cannot add acquisitions when images are present.")

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
            # This lovely roundabout way of reading a waveform header is due largely to h5's handling
            # of padding and alignment. Nu guarantees are given, so we need create a structured array
            # with a header to have the contents is filled in correctly. We start with an array of
            # zeroes to avoid garbage in the padding bytes.
            header_array = numpy.zeros((1, ), dtype=waveform_header_dtype)
            header_array[0] = raw['head']

            waveform = Waveform(header_array)
            waveform.data[:] = raw['data'].view(np.uint32).reshape(
                (waveform.channels,
                 waveform.number_of_samples)
            )[:]

            yield waveform

    def __set_waveforms(self, waveforms):

        if self.has_images():
            raise TypeError("Cannot add waveforms when images are present.")

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

        if self.has_data():
            raise TypeError("Cannot add images when data is present.")

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

    class Arrays:

        def __init__(self, contents):
            self.__contents = contents

        def __getitem__(self, key):
            item = self.__contents.get(key, None)
            if not isinstance(item, h5py.Dataset):
                raise KeyError("Key {} does not map to an array.".format(key))
            return numpy.array(item, copy=True)

        def __delitem__(self, key):
            del self.__contents[key]

        def __setitem__(self, key, value):
            self.__contents[key] = value

        def __iter__(self):
            for key, item in self.__contents.items():
                if isinstance(item, h5py.Dataset):
                    yield key

        def __str__(self):
            return str([key for key in self])

    def __get_arrays(self):
        return Container.Arrays(self.__contents)

    arrays = property(__get_arrays)

    def __get_header(self):
        if 'xml' not in self.__contents:
            return None
        return ismrmrd.xsd.CreateFromDocument(self.__contents['xml'][0])

    def __set_header(self, header):
        self.__del_header()
        self.__contents.create_dataset('xml', shape=(1, ), dtype=h5py.special_dtype(vlen=str))
        self.__contents['xml'][0] = header.toxml('utf-8')

    def __del_header(self):
        if 'xml' in self.__contents:
            del self.__contents['xml']

    header = property(__get_header, __set_header, __del_header)

    def has_header(self):
        return 'xml' in self.__contents

    def has_images(self):
        return all((key in self.__contents for key in ['data', 'headers', 'attributes']))

    def has_data(self):
        return any((self.has_acquisitions(), self.has_waveforms()))

    def has_waveforms(self):
        return 'waveforms' in self.__contents

    def has_acquisitions(self):
        return 'data' in self.__contents and not self.has_images()

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
