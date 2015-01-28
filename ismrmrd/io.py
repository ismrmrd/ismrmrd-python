import h5py
import numpy as np
import ismrmrd

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
    def number_of_aquisitions(self):
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
        
        # create an acquisition header and fill it
        hdr = ismrmrd.AcquisitionHeader()
        h5hdr = self.__dset['data'][acqnum]['head']
        hdr.version = h5hdr['version']
        hdr.flags = h5hdr['flags']
        hdr.measurement_uid =  h5hdr['measurement_uid']
        hdr.scan_counter = h5hdr['scan_counter']
        hdr.acquisition_time_stamp =  h5hdr['acquisition_time_stamp']
        for n in range(ismrmrd.PHYS_STAMPS):
            hdr.physiology_time_stamp[n] =  h5hdr['physiology_time_stamp'][n]
        hdr.number_of_samples =  h5hdr['number_of_samples']
        hdr.available_channels =  h5hdr['available_channels']
        hdr.active_channels =  h5hdr['active_channels']
        for n in range(ismrmrd.CHANNEL_MASKS):
            hdr.channel_mask[n] =  h5hdr['channel_mask'][n]
        hdr.discard_pre =  h5hdr['discard_pre']
        hdr.discard_post =  h5hdr['discard_post']
        hdr.center_sample =  h5hdr['center_sample']
        hdr.encoding_space_ref =  h5hdr['encoding_space_ref']
        hdr.trajectory_dimensions =  h5hdr['trajectory_dimensions']
        hdr.sample_time_us =  h5hdr['sample_time_us']
        for n in range(ismrmrd.POSITION_LENGTH):
            hdr.position[n] =  h5hdr['position'][n]
        for n in range(ismrmrd.DIRECTION_LENGTH):
            hdr.read_dir[n] =  h5hdr['read_dir'][n]
        for n in range(ismrmrd.DIRECTION_LENGTH):
            hdr.phase_dir[n] =  h5hdr['phase_dir'][n]
        for n in range(ismrmrd.DIRECTION_LENGTH):
            hdr.slice_dir[n] =  h5hdr['slice_dir'][n]
        for n in range(ismrmrd.POSITION_LENGTH):
            hdr.patient_table_position[n] =  h5hdr['patient_table_position'][n]
        hdr.idx.kspace_encode_step_1 =  h5hdr['idx']['kspace_encode_step_1']
        hdr.idx.kspace_encode_step_2 =  h5hdr['idx']['kspace_encode_step_2']
        hdr.idx.average =  h5hdr['idx']['average']
        hdr.idx.slice =  h5hdr['idx']['slice']
        hdr.idx.contrast =  h5hdr['idx']['contrast']
        hdr.idx.phase =  h5hdr['idx']['phase']
        hdr.idx.repetition =  h5hdr['idx']['repetition']
        hdr.idx.set =  h5hdr['idx']['set']
        hdr.idx.segment =  h5hdr['idx']['segment']
        for n in range(ismrmrd.USER_INTS):
            hdr.idx.user[n] =  h5hdr['idx']['user'][n]
        for n in range(ismrmrd.USER_INTS):
            hdr.user_int[n] =  h5hdr['user_int'][n]
        for n in range(ismrmrd.USER_FLOATS):
            hdr.user_float[n] =  h5hdr['user_float'][n]

        # create a new acquisition
        acq = ismrmrd.Acquisition()

        # set the header
        # this sets the size for the aquisition's data and trajectory arrays
        acq.setHead(hdr)
        
        # copy the data as complex float
        acq.data[:] = self.__dset['data'][acqnum]['data'].view(np.complex64).reshape((hdr.active_channels, hdr.number_of_samples))[:]
        
        # copy the trajectory as float
        if acq.traj.size>0:
            acq.traj[:] = self.__dset['data'][acqnum]['traj'].reshape((hdr.number_of_samples,hdr.trajectory_dimensions))[:]
        
        return acq
