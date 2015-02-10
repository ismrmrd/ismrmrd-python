import h5py
import numpy as np
import ismrmrd

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

class Dataset(object):
    def __init__(self, filename, dataset_name="dataset", create_if_needed=True):
        # Open the file
        if create_if_needed:
            self.__file = h5py.File(filename,'a')
        else:
            self.__file = h5py.File(filename,'r+')

        # Open/Create the toplevel dataset group
        self.__dset = self.__file.require_group(dataset_name)
            
    def close(self):
        if self.__file.fid:
            self.__file.close()

    @property
    def number_of_acquisitions(self):
        return self.__dset['data'].size

    def read_xml_header(self):
        if 'xml' in self.__dset:
            try:
                return self.__dset['xml'][0]
            except:
                print("Error reading XML header from the dataset.")
                raise
        else:
            raise LookupError("XML header not found in the dataset.")

    def write_xml_header(self,xmlstring):
        dset = self.__dset.require_dataset('xml',shape=(1,), dtype=h5py.special_dtype(vlen=str))
        dset[0] = xmlstring

    def read_acquisition(self, acqnum):
        
        # create an acquisition
        # and fill with the header for this acquisition
        acq = ismrmrd.Acquisition(self.__dset['data'][acqnum]['head'])

        # copy the data as complex float
        acq.data[:] = self.__dset['data'][acqnum]['data'].view(np.complex64).reshape((acq.active_channels, acq.number_of_samples))[:]

        # copy the trajectory as float
        if acq.traj.size>0:
            acq.traj[:] = self.__dset['data'][acqnum]['traj'].reshape((acq.number_of_samples,acq.trajectory_dimensions))[:]
        
        return acq
    

    def append_acquisition(self, acq):
        # extend by 1
        if 'data' in self.__dset:
            acqnum = self.__dset['data'].shape[0]
            self.__dset['data'].resize(acqnum+1,axis=0)
        else:
            self.__dset.create_dataset("data", (1,), maxshape=(None,), dtype=acquisition_dtype)
            acqnum = 0
        
        # create an empty hdf5 acquisition and fill it
        h5acq = np.empty((1,),dtype=acquisition_dtype)
        # copy the header
        h5acq[0]['head'] = buffer(acq.getHead());
        # copy the data as float
        h5acq[0]['data'] = acq.data.view(np.float32).reshape((2*acq.active_channels*acq.number_of_samples,))
        
        # copy the trajectory as float
        h5acq[0]['traj'] = acq.traj.view(np.float32).reshape((acq.number_of_samples*acq.trajectory_dimensions,))

        # put it into the hdf5 file
        self.__dset['data'][acqnum] = h5acq[0]
