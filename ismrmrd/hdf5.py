import h5py
import numpy as np
import ismrmrd

from .constants import *

# For Python 2.7 ctypes bug
import warnings

encoding_counters_dtype = np.dtype(
       [('kspace_encode_step_1', '<u2'),
        ('kspace_encode_step_2', '<u2'),
        ('average', '<u2'),
        ('slice', '<u2'),
        ('contrast', '<u2'),
        ('phase', '<u2'),
        ('repetition', '<u2'),
        ('set', '<u2'),
        ('segment', '<u2'),
        ('user', '<u2', (8,))])

acquisition_header_dtype = np.dtype(
     [('version', '<u2'),
      ('flags', '<u8'),
      ('measurement_uid', '<u4'),
      ('scan_counter', '<u4'),
      ('acquisition_time_stamp', '<u4'),
      ('physiology_time_stamp', '<u4', (3,)),
      ('number_of_samples', '<u2'),
      ('available_channels', '<u2'),
      ('active_channels', '<u2'),
      ('channel_mask', '<u8', (16,)),
      ('discard_pre', '<u2'),
      ('discard_post', '<u2'),
      ('center_sample', '<u2'),
      ('encoding_space_ref', '<u2'),
      ('trajectory_dimensions', '<u2'),
      ('sample_time_us', '<f4'),
      ('position', '<f4', (3,)),
      ('read_dir', '<f4', (3,)),
      ('phase_dir', '<f4', (3,)),
      ('slice_dir', '<f4', (3,)),
      ('patient_table_position', '<f4', (3,)),
      ('idx', encoding_counters_dtype),
      ('user_int', '<i4', (8,)),
      ('user_float', '<f4', (8,))])

acquisition_dtype = np.dtype(
    [('head', acquisition_header_dtype),
     ('traj', h5py.special_dtype(vlen=np.dtype('float32'))),
     ('data', h5py.special_dtype(vlen=np.dtype('float32')))])

image_header_dtype = np.dtype(
    [('version', '<u2'),
     ('data_type', '<u2'),
     ('flags', '<u8'),
     ('measurement_uid', '<u4'),
     ('matrix_size', '<u2', (3,)),
     ('field_of_view', '<f4', (3,)),
     ('channels', '<u2'),
     ('position', '<f4', (3,)),
     ('read_dir', '<f4', (3,)),
     ('phase_dir', '<f4', (3,)),
     ('slice_dir', '<f4', (3,)),
     ('patient_table_position', '<f4', (3,)),
     ('average', '<u2'),
     ('slice', '<u2'),
     ('contrast', '<u2'),
     ('phase', '<u2'),
     ('repetition', '<u2'),
     ('set', '<u2'),
     ('acquisition_time_stamp', '<u4'),
     ('physiology_time_stamp', '<u4', (3,)),
     ('image_type', '<u2'),
     ('image_index', '<u2'),
     ('image_series_index', '<u2'),
     ('user_int', '<i4', (8,)),
     ('user_float', '<f4', (8,)),
     ('attribute_string_len', '<u4')])

# hdf5 data type lookup function
def get_hdf5type(val):
    if val == DATATYPE_USHORT:
        return np.dtype('<u2')
    elif val == DATATYPE_SHORT:
        return np.dtype('<i2')
    elif val == DATATYPE_UINT:
        return np.dtype('<u4')
    elif val == DATATYPE_INT:
        return np.dtype('<i4')
    elif val == DATATYPE_FLOAT:
        return np.dtype('<f4')
    elif val == DATATYPE_DOUBLE:
        return np.dtype('<f8')
    elif val == DATATYPE_CXFLOAT:
        return np.dtype([('real','<f4'),('imag','<f4')])
    elif val == DATATYPE_CXDOUBLE:
        return np.dtype([('real','<f8'),('imag','<f8')])
    else:
        raise TypeError("Unknown data type.")

def get_arrayhdf5type(val):
    if val == np.uint16:
        return np.dtype('<u2')
    elif val == np.int16:
        return np.dtype('<i2')
    elif val == np.uint32:
        return np.dtype('<u4')
    elif val == np.int32:
        return np.dtype('<i4')
    elif val == np.float32:
        return np.dtype('<f4')
    elif val == np.float64:
        return np.dtype('<f8')
    elif val == np.complex64:
        return np.dtype([('real','<f4'),('imag','<f4')])
    elif val == np.complex128:
        return np.dtype([('real','<f8'),('imag','<f8')])
    else:
        raise TypeError("Unsupported data type.")    
    
def fileinfo(fname):
    fid = h5py.File(fname,'r')
    retval = fid.keys()
    fid.close()
    return retval


class Dataset(object):
    def __init__(self, filename, dataset_name="dataset", create_if_needed=True):
        # Open the file
        if create_if_needed:
            self._file = h5py.File(filename,'a')
        else:
            self._file = h5py.File(filename,'r+')

        self._dataset_name = dataset_name

    def __del__(self):
        try:
            self.close()
        except:
            pass
        
    @property
    def _dataset(self):
        if self._dataset_name not in self._file:
            raise LookupError("Dataset not found in the hdf5 file.")
        return self._file[self._dataset_name]

    def list(self):
        return self._dataset.keys()
    
    def close(self):
        #TODO do we want to flush the file?
        #self._file.flush()
        self._file.close()

    def read_xml_header(self):
        if 'xml' not in self._dataset:
            raise LookupError("XML header not found in the dataset.")
        return self._dataset['xml'][0]

    def write_xml_header(self,xmlstring):
        # create the dataset if needed
        self._file.require_group(self._dataset_name)

        dset = self._dataset.require_dataset('xml',shape=(1,), dtype=h5py.special_dtype(vlen=str))
        dset[0] = xmlstring

    def number_of_acquisitions(self):
        if 'data' not in self._dataset:
            raise LookupError("Acquisition data not found in the dataset.")
        return self._dataset['data'].size

    def read_acquisition(self, acqnum):
        if 'data' not in self._dataset:
            raise LookupError("Acquisition data not found in the dataset.")
        
        # create an acquisition
        # and fill with the header for this acquisition
        acq = ismrmrd.Acquisition(self._dataset['data'][acqnum]['head'])

        # copy the data as complex float
        acq.data[:] = self._dataset['data'][acqnum]['data'].view(np.complex64).reshape((acq.active_channels, acq.number_of_samples))[:]

        # copy the trajectory as float
        if acq.traj.size>0:
            acq.traj[:] = self._dataset['data'][acqnum]['traj'].reshape((acq.number_of_samples,acq.trajectory_dimensions))[:]

        return acq

    def append_acquisition(self, acq):
        # create the dataset if needed
        self._file.require_group(self._dataset_name)
        
        # extend by 1
        if 'data' in self._dataset:
            acqnum = self._dataset['data'].shape[0]
            self._dataset['data'].resize(acqnum+1,axis=0)
        else:
            self._dataset.create_dataset("data", (1,), maxshape=(None,), dtype=acquisition_dtype)
            acqnum = 0
        
        # create an empty hdf5 acquisition and fill it
        h5acq = np.empty((1,),dtype=acquisition_dtype)
        # copy the header

        #Python 2.7 has a bug in ctypes buffer size http://bugs.python.org/issue10744
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            h5acq[0]['head'] = acq.getHead();
        
        # copy the data as float
        h5acq[0]['data'] = acq.data.view(np.float32).reshape((2*acq.active_channels*acq.number_of_samples,))
        
        # copy the trajectory as float
        h5acq[0]['traj'] = acq.traj.view(np.float32).reshape((acq.number_of_samples*acq.trajectory_dimensions,))

        # put it into the hdf5 file
        self._dataset['data'][acqnum] = h5acq[0]

    def number_of_images(self, impath):
        if impath not in self._dataset:
            raise LookupError("Image data not found in the dataset.")
        return self._dataset[impath]['header'].shape[0]
    
    def read_image(self, impath, imnum):
        if impath not in self._dataset:
            raise LookupError("Image data not found in the dataset.")
        
        # create an image
        # and fill with the header and attribute string for this image
        im = ismrmrd.Image(self._dataset[impath]['header'][imnum], self._dataset[impath]['attributes'][imnum])

        # copy the data
        # ismrmrd complex data is stored as pairs named real and imag
        # TODO do we need to store and reset or the config local to the module?
        cplxcfg = h5py.get_config().complex_names;
        h5py.get_config().complex_names = ('real','imag')
        im.data[:] = self._dataset[impath]['data'][imnum]
        h5py.get_config().complex_names = cplxcfg

        return im
    
    def append_image(self, impath, im):
        # create the dataset if needed
        self._file.require_group(self._dataset_name)

        # create the image if needed
        self._dataset.require_group(impath)
        
        # extend by 1
        if 'header' in self._dataset[impath]:
            imnum = self._dataset[impath]['header'].shape[0]
            # check that they are all equal
            self._dataset[impath]['header'].resize(imnum+1,axis=0)
            self._dataset[impath]['attributes'].resize(imnum+1,axis=0)
            self._dataset[impath]['data'].resize(imnum+1,axis=0)
        else:
            self._dataset[impath].create_dataset("header", (1,), maxshape=(None,), dtype=image_header_dtype)
            self._dataset[impath].create_dataset("attributes", (1,), maxshape=(None,), dtype=h5py.special_dtype(vlen=str))
            self._dataset[impath].create_dataset("data", (1,im.data.shape[0],im.data.shape[1],im.data.shape[2],im.data.shape[3]),
                                                maxshape=(None,im.data.shape[0],im.data.shape[1],im.data.shape[2],im.data.shape[3]), dtype=get_hdf5type(im.data_type))
            imnum = 0
        
        # put the header
        # this should probably be done better
        h5imhead = np.empty((1,),dtype=image_header_dtype)
        
        #Python 2.7 has a bug in ctypes buffer size http://bugs.python.org/issue10744
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            h5imhead[0] = buffer(im.getHead())
        
        self._dataset[impath]['header'][imnum] = h5imhead[0]
        # put the attribute string
        self._dataset[impath]['attributes'][imnum] = im.attribute_string
        # put the data
        self._dataset[impath]['data'][imnum] = im.data.view(dtype=get_hdf5type(im.data_type))

    def number_of_arrays(self, arrpath):
        if arrpath not in self._dataset:
            raise LookupError("Array data not found in the dataset.")
        return self._dataset[arrpath].shape[0]
    
    def read_array(self, arrpath, arrnum):
        if arrpath not in self._dataset:
            raise LookupError("Array data not found in the dataset.")
        
        # ismrmrd complex data is stored as pairs named real and imag
        # TODO do we need to store and reset or the config local to the module?
        cplxcfg = h5py.get_config().complex_names;
        h5py.get_config().complex_names = ('real','imag')
        arr = np.copy(self._dataset[arrpath][arrnum])
        h5py.get_config().complex_names = cplxcfg

        return arr
    
    def append_array(self, arrpath, arr):
        # create the dataset if needed
        self._file.require_group(self._dataset_name)

        # extend by 1
        if arrpath in self._dataset:
            arrnum = self._dataset[arrpath].shape[0]
            self._dataset[arrpath].resize(arrnum+1,axis=0)
        else:
            shape = list(arr.shape)
            shape.insert(0,1)            
            shape = tuple(shape)
            maxshape = list(arr.shape)
            maxshape.insert(0,None)
            maxshape = tuple(maxshape)
            self._dataset.create_dataset(arrpath, shape, maxshape=maxshape, dtype=get_arrayhdf5type(arr.dtype))
            arrnum = 0
        
        # put the data
        self._dataset[arrpath][arrnum] = arr.view(dtype=get_arrayhdf5type(arr.dtype))

