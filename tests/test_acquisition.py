import ismrmrd
import ctypes
import numpy as np

from nose.tools import eq_

def test_encoding_counters():
    idx = ismrmrd.EncodingCounters()
    eq_(ctypes.sizeof(idx), 34)

def test_header():
    head = ismrmrd.AcquisitionHeader()
    eq_(ctypes.sizeof(head), 340)

def test_new_instance():
    acq = ismrmrd.Acquisition()
    eq_(type(acq.getHead()), ismrmrd.AcquisitionHeader)
    eq_(type(acq.data), np.ndarray)
    eq_(acq.data.dtype, np.complex64)
    eq_(type(acq.traj), np.ndarray)
    eq_(acq.traj.dtype, np.float32)

def test_read_only_fields():
    acq = ismrmrd.Acquisition()
    # test read-only fields
    for field in ['number_of_samples', 'active_channels', 'trajectory_dimensions']:
        try:
            setattr(acq, field, None)
        except:
            pass
        else:
            assert False, "assigned to read-only field of Acquisition"

def test_resize():
    acq = ismrmrd.Acquisition()
    nsamples, nchannels, ntrajdims = 128, 8, 3
    acq.resize(nsamples, nchannels, ntrajdims)
    eq_(acq.data.shape, (nchannels, nsamples))
    eq_(acq.traj.shape, (nsamples, ntrajdims))
    head = acq.getHead()
    eq_(head.number_of_samples, nsamples)
    eq_(head.active_channels, nchannels)
    eq_(head.trajectory_dimensions, ntrajdims)

def test_set_head():
    acq = ismrmrd.Acquisition()
    head = ismrmrd.AcquisitionHeader()
    nsamples, nchannels, ntrajdims = 128, 8, 3
    head.number_of_samples = nsamples
    head.active_channels = nchannels
    head.trajectory_dimensions = ntrajdims

    acq.setHead(head)

    eq_(acq.data.shape, (nchannels, nsamples))
    eq_(acq.traj.shape, (nsamples, ntrajdims))

def test_flags():
    acq = ismrmrd.Acquisition()
    eq_(acq.flags, 0)

    for i in range(1, 65):
        eq_(acq.isFlagSet(i), False)

    for i in range(1, 65):
        acq.setFlag(i)
        eq_(acq.isFlagSet(i), True)

    for i in range(1, 65):
        eq_(acq.isFlagSet(i), True)

    for i in range(1, 65):
        acq.clearFlag(i)
        eq_(acq.isFlagSet(i), False)

    eq_(acq.flags, 0)

    for i in range(1, 65):
        acq.setFlag(i)
    acq.clearAllFlags()
    for i in range(1, 65):
        eq_(acq.isFlagSet(i), False)
