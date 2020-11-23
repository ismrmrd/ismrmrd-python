import h5py
import numpy

from .hdf5 import *
from .acquisition import *
from .waveform import *
from .image import *
from .xsd import ToXML


class DataWrapper:

    def __init__(self, data):
        self.data = data

    def __len__(self):
        return self.data.size

    def __iter__(self):
        for raw in self.data:
            yield self.from_numpy(raw)

    def __getitem__(self, key):
        if isinstance(key, slice):
            return [self.from_numpy(raw) for raw in self.data[key]]
        else:
            return self.from_numpy(self.data[key])

    def __setitem__(self, key, value):
        try:
            iterable = [self.to_numpy(v) for v in value]
        except TypeError:
            iterable = [self.to_numpy(value)]

        self.data[key] = numpy.array(iterable, dtype=self.datatype)

    def __repr__(self):
        return type(self).__name__ + " containing " + self.data.__repr__()

    @classmethod
    def from_numpy(cls, raw):
        raise NotImplemented()

    @classmethod
    def to_numpy(cls, item):
        raise NotImplemented()

    datatype = None


class Acquisitions(DataWrapper):

    def __init__(self, data):
        super().__init__(data)

    @classmethod
    def from_numpy(cls, raw):
        acquisition = Acquisition(raw['head'])

        acquisition.data[:] = raw['data'].view(np.complex64).reshape(
            (acquisition.active_channels,
             acquisition.number_of_samples)
        )[:]

        acquisition.traj[:] = raw['traj'].reshape(
            (acquisition.number_of_samples,
             acquisition.trajectory_dimensions)
        )[:]

        return acquisition

    @classmethod
    def to_numpy(cls, acq):
        return (
            np.frombuffer(acq.getHead(), dtype=acquisition_header_dtype),
            acq.traj.view(np.float32).reshape((acq.number_of_samples * acq.trajectory_dimensions,)),
            acq.data.view(np.float32).reshape((2 * acq.active_channels * acq.number_of_samples,))
        )

    datatype = acquisition_dtype


class Waveforms(DataWrapper):

    def __init__(self, data):
        super().__init__(data)

    @classmethod
    def from_numpy(cls, raw):
        # This lovely roundabout way of reading a waveform header is due largely to h5's handling
        # of padding and alignment. Nu guarantees are given, so we need create a structured array
        # with a header to have the contents filled in correctly. We start with an array of
        # zeroes to avoid garbage in the padding bytes.
        header_array = numpy.zeros((1,), dtype=waveform_header_dtype)
        header_array[0] = raw['head']

        waveform = Waveform(header_array)
        waveform.data[:] = raw['data'].view(np.uint32).reshape(
            (waveform.channels,
             waveform.number_of_samples)
        )[:]

        return waveform

    @classmethod
    def to_numpy(cls, wav):
        return (
            np.frombuffer(wav.getHead(), dtype=waveform_header_dtype),
            wav.data.view(np.uint32).reshape((wav.channels * wav.number_of_samples,))
        )

    datatype = waveform_dtype


class Images:

    def __init__(self, data, headers, attributes):
        self.data = data
        self.headers = headers
        self.attributes = attributes

    def __len__(self):
        return self.headers.size

    def __iter__(self):
        for data, header, attributes in zip(self.data, self.headers, self.attributes):
            yield self.from_numpy(header, data, attributes)

    def __getitem__(self, key):
        if isinstance(key, slice):
            return [self.from_numpy(*raw) for raw in zip(self.headers[key], self.data[key], self.attributes[key])]
        else:
            return self.from_numpy(
                self.headers[key],
                self.data[key],
                self.attributes[key]
            )

    def __setitem__(self, key, value):
        try:
            iterable = [self.to_numpy(v) for v in value]
        except TypeError:
            iterable = [self.to_numpy(value)]

        self.headers[key] = numpy.stack([header for header, _, __ in iterable])
        self.data[key] = numpy.stack([data for _, data, __ in iterable])
        self.attributes[key] = numpy.stack([attributes for _, __, attributes in iterable])

    @classmethod
    def from_numpy(cls, header, data, attributes):
        image = Image(header, attributes.decode('ascii', 'strict'))
        image.data[:] = data.astype(image.data.dtype)
        return image

    @classmethod
    def to_numpy(cls, image):
        header = np.frombuffer(image.getHead(), dtype=image_header_dtype)
        data = image.data
        attributes = image.attribute_string.encode(encoding='ascii', errors='strict')

        return header, data, attributes

    datatype = None


class Folder:
    def __init__(self, contents):
        self._contents = contents

    def __getitem__(self, key):
        if key in self._contents:
            return Container(self._contents[key])
        return self.__missing__(key)

    def __delitem__(self, key):
        if key in self._contents:
            del self._contents[key]

    def __missing__(self, key):
        return Container(self._contents.require_group(key))

    def __contains__(self, key):
        return key in self._contents

    def __iter__(self):
        for key, item in self._contents.items():
            if isinstance(item, h5py.Group):
                yield key

    def __str__(self):
        return str([key for key in self._contents])

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

    def keys(self):
        return self._contents.keys()


class Container(Folder):

    def __init__(self, contents):
        super(Container, self).__init__(contents)

    def __get_acquisitions(self):
        if not self.has_acquisitions():
            return None
        data = self._contents.get('data')
        return Acquisitions(data)

    def __set_acquisitions(self, acquisitions):

        if self.has_images():
            raise TypeError("Cannot add acquisitions when images are present.")

        buffer = numpy.array([Acquisitions.to_numpy(a) for a in acquisitions], dtype=acquisition_dtype)

        self.__del_acquisitions()
        self._contents['data'] = buffer

    def __del_acquisitions(self):
        if 'data' in self._contents:
            del self._contents['data']

    acquisitions = property(__get_acquisitions, __set_acquisitions, __del_acquisitions)

    def __get_waveforms(self):
        if not self.has_waveforms():
            return None
        data = self._contents.get('waveforms')
        return Waveforms(data)

    def __set_waveforms(self, waveforms):

        if self.has_images():
            raise TypeError("Cannot add waveforms when images are present.")

        converter = Waveforms(None)
        buffer = numpy.array([converter.to_numpy(w) for w in waveforms], dtype=waveform_dtype)

        self.__del_waveforms()
        self._contents['waveforms'] = buffer

    def __del_waveforms(self):
        if 'waveforms' in self._contents:
            del self._contents['waveforms']

    waveforms = property(__get_waveforms, __set_waveforms, __del_waveforms)

    def __get_images(self):
        if not self.has_images():
            return None

        return Images(
            self._contents.get('data'),
            self._contents.get('header'),
            self._contents.get('attributes')
        )

    def __set_images(self, images):

        if self.has_data():
            raise TypeError("Cannot add images when data is present.")

        images = list(images)

        data = numpy.stack([image.data for image in images])
        headers = numpy.stack([np.frombuffer(image.getHead(), dtype=image_header_dtype) for image in images])
        attributes = numpy.stack([image.attribute_string for image in images])

        self.__del_images()
        self._contents.create_dataset('data', data=data)
        self._contents.create_dataset('header', data=headers)
        self._contents.create_dataset('attributes', shape=attributes.shape, dtype=h5py.special_dtype(vlen=bytes))
        self._contents['attributes'][:] = attributes

    def __del_images(self):
        for key in ['header', 'data', 'attributes']:
            if key in self._contents:
                del self._contents[key]

    images = property(__get_images, __set_images, __del_images)

    def __get_header(self):
        if not self.has_header():
            return None
        return ismrmrd.xsd.CreateFromDocument(self._contents['xml'][0])

    def __set_header(self, header):
        self.__del_header()
        self._contents.create_dataset('xml', shape=(1,), dtype=h5py.special_dtype(vlen=bytes))
        self._contents['xml'][0] = ToXML(header)

    def __del_header(self):
        if 'xml' in self._contents:
            del self._contents['xml']

    header = property(__get_header, __set_header, __del_header)

    def available(self):

        def header():
            if self.has_header():
                return 'header'

        def acquisitions():
            if self.has_acquisitions():
                return 'acquisitions'

        def waveforms():
            if self.has_waveforms():
                return 'waveforms'

        def images():
            if self.has_images():
                return 'images'

        return list(filter(bool, [header(), acquisitions(), waveforms(), images()]))

    def has_header(self):
        return 'xml' in self._contents

    def has_images(self):
        return all((key in self._contents for key in ['data', 'header', 'attributes']))

    def has_data(self):
        return any((self.has_acquisitions(), self.has_waveforms()))

    def has_waveforms(self):
        return 'waveforms' in self._contents

    def has_acquisitions(self):
        return 'data' in self._contents and not self.has_images()


class File(Folder):

    def __init__(self, filename, mode='a'):
        self.__file = h5py.File(filename, mode)
        super().__init__(self.__file)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.__file.close()
