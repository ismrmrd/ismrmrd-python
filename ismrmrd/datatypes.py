import numpy as np
import h5py

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
