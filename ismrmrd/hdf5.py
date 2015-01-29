import h5py
import numpy as np
import ismrmrd

acquisition_dtype = np.dtype(
    [('head',
     [('version', '<u2'),
      ('flags', '<u8'),
      ('measurement_uid', '<u4'),
      ('scan_counter', '<u4'),
      ('acquisition_time_stamp', '<u4'),
      ('physiology_time_stamp', '<u4', (ismrmrd.PHYS_STAMPS,)),
      ('number_of_samples', '<u2'),
      ('available_channels', '<u2'),
      ('active_channels', '<u2'),
      ('channel_mask', '<u8', (ismrmrd.CHANNEL_MASKS,)),
      ('discard_pre', '<u2'),
      ('discard_post', '<u2'),
      ('center_sample', '<u2'),
      ('encoding_space_ref', '<u2'),
      ('trajectory_dimensions', '<u2'),
      ('sample_time_us', '<f4'),
      ('position', '<f4', (ismrmrd.POSITION_LENGTH,)),
      ('read_dir', '<f4', (ismrmrd.DIRECTION_LENGTH,)),
      ('phase_dir', '<f4', (ismrmrd.DIRECTION_LENGTH,)),
      ('slice_dir', '<f4', (ismrmrd.DIRECTION_LENGTH,)),
      ('patient_table_position', '<f4', (ismrmrd.POSITION_LENGTH,)),
      ('idx',
       [('kspace_encode_step_1', '<u2'),
        ('kspace_encode_step_2', '<u2'),
        ('average', '<u2'), ('slice', '<u2'),
        ('contrast', '<u2'), ('phase', '<u2'),
        ('repetition', '<u2'), ('set', '<u2'),
        ('segment', '<u2'),
        ('user', '<u2', (ismrmrd.USER_INTS,))]),
      ('user_int', '<i4', (ismrmrd.USER_INTS,)),
      ('user_float', '<f4', (ismrmrd.USER_FLOATS,))]),
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
        acq = ismrmrd.Acquisition()

        # grab a shortcut to the header in the hdf5 file        
        h5hdr = self.__dset['data'][acqnum]['head']
        
        # set the size
        acq.resize(h5hdr['number_of_samples'], h5hdr['active_channels'], h5hdr['trajectory_dimensions'])

        # set the rest of the header fields        
        acq.version = h5hdr['version']
        acq.flags = h5hdr['flags']
        acq.measurement_uid =  h5hdr['measurement_uid']
        acq.scan_counter = h5hdr['scan_counter']
        acq.acquisition_time_stamp =  h5hdr['acquisition_time_stamp']
        for n in range(ismrmrd.PHYS_STAMPS):
            acq.physiology_time_stamp[n] =  h5hdr['physiology_time_stamp'][n]
        acq.available_channels =  h5hdr['available_channels']
        for n in range(ismrmrd.CHANNEL_MASKS):
            acq.channel_mask[n] =  h5hdr['channel_mask'][n]
        acq.discard_pre =  h5hdr['discard_pre']
        acq.discard_post =  h5hdr['discard_post']
        acq.center_sample =  h5hdr['center_sample']
        acq.encoding_space_ref =  h5hdr['encoding_space_ref']
        acq.sample_time_us =  h5hdr['sample_time_us']
        for n in range(ismrmrd.POSITION_LENGTH):
            acq.position[n] =  h5hdr['position'][n]
        for n in range(ismrmrd.DIRECTION_LENGTH):
            acq.read_dir[n] =  h5hdr['read_dir'][n]
        for n in range(ismrmrd.DIRECTION_LENGTH):
            acq.phase_dir[n] =  h5hdr['phase_dir'][n]
        for n in range(ismrmrd.DIRECTION_LENGTH):
            acq.slice_dir[n] =  h5hdr['slice_dir'][n]
        for n in range(ismrmrd.POSITION_LENGTH):
            acq.patient_table_position[n] =  h5hdr['patient_table_position'][n]
        acq.idx.kspace_encode_step_1 =  h5hdr['idx']['kspace_encode_step_1']
        acq.idx.kspace_encode_step_2 =  h5hdr['idx']['kspace_encode_step_2']
        acq.idx.average =  h5hdr['idx']['average']
        acq.idx.slice =  h5hdr['idx']['slice']
        acq.idx.contrast =  h5hdr['idx']['contrast']
        acq.idx.phase =  h5hdr['idx']['phase']
        acq.idx.repetition =  h5hdr['idx']['repetition']
        acq.idx.set =  h5hdr['idx']['set']
        acq.idx.segment =  h5hdr['idx']['segment']
        for n in range(ismrmrd.USER_INTS):
            acq.idx.user[n] =  h5hdr['idx']['user'][n]
        for n in range(ismrmrd.USER_INTS):
            acq.user_int[n] =  h5hdr['user_int'][n]
        for n in range(ismrmrd.USER_FLOATS):
            acq.user_float[n] =  h5hdr['user_float'][n]

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
        # first the header
        h5acq[0]['head']['version'] = acq.version
        h5acq[0]['head']['flags'] = acq.flags
        h5acq[0]['head']['measurement_uid'] = acq.measurement_uid
        h5acq[0]['head']['scan_counter'] = acq.scan_counter
        h5acq[0]['head']['acquisition_time_stamp'] = acq.acquisition_time_stamp
        for n in range(ismrmrd.PHYS_STAMPS):
            h5acq[0]['head']['physiology_time_stamp'][n] = acq.physiology_time_stamp[n]
        h5acq[0]['head']['number_of_samples'] = acq.number_of_samples
        h5acq[0]['head']['available_channels'] = acq.available_channels
        h5acq[0]['head']['active_channels'] = acq.active_channels
        for n in range(ismrmrd.CHANNEL_MASKS):
            h5acq[0]['head']['channel_mask'][n] = acq.channel_mask[n]
        h5acq[0]['head']['discard_pre'] = acq.discard_pre
        h5acq[0]['head']['discard_post'] = acq.discard_post
        h5acq[0]['head']['center_sample'] = acq.center_sample
        h5acq[0]['head']['encoding_space_ref'] = acq.encoding_space_ref
        h5acq[0]['head']['trajectory_dimensions'] = acq.trajectory_dimensions
        h5acq[0]['head']['sample_time_us'] = acq.sample_time_us
        for n in range(ismrmrd.POSITION_LENGTH):
            h5acq[0]['head']['position'][n] = acq.position[n]
        for n in range(ismrmrd.DIRECTION_LENGTH):
            h5acq[0]['head']['read_dir'][n] = acq.read_dir[n]
        for n in range(ismrmrd.DIRECTION_LENGTH):
            h5acq[0]['head']['phase_dir'][n] = acq.phase_dir[n]
        for n in range(ismrmrd.DIRECTION_LENGTH):
            h5acq[0]['head']['slice_dir'][n] = acq.slice_dir[n]
        for n in range(ismrmrd.POSITION_LENGTH):
            h5acq[0]['head']['patient_table_position'][n] = acq.patient_table_position[n]
        h5acq[0]['head']['idx']['kspace_encode_step_1'] = acq.idx.kspace_encode_step_1
        h5acq[0]['head']['idx']['kspace_encode_step_2'] = acq.idx.kspace_encode_step_2
        h5acq[0]['head']['idx']['average'] = acq.idx.average
        h5acq[0]['head']['idx']['slice'] = acq.idx.slice
        h5acq[0]['head']['idx']['contrast'] = acq.idx.contrast
        h5acq[0]['head']['idx']['phase'] = acq.idx.phase
        h5acq[0]['head']['idx']['repetition'] = acq.idx.repetition
        h5acq[0]['head']['idx']['set'] = acq.idx.set
        h5acq[0]['head']['idx']['segment'] = acq.idx.segment
        for n in range(ismrmrd.USER_INTS):
            h5acq[0]['head']['idx']['user'][n] = acq.idx.user[n]
        for n in range(ismrmrd.USER_INTS):
            h5acq[0]['head']['user_int'][n] = acq.user_int[n]
        for n in range(ismrmrd.USER_FLOATS):
            h5acq[0]['head']['user_float'][n] = acq.user_float[n]

        # copy the data as float
        h5acq[0]['data'] = acq.data.view(np.float32).reshape((2*acq.active_channels*acq.number_of_samples,))
        
        # copy the trajectory as float
        h5acq[0]['traj'] = acq.traj.view(np.float32).reshape((acq.number_of_samples*acq.trajectory_dimensions,))

        # put it into the hdf5 file
        self.__dset['data'][acqnum] = h5acq[0]
