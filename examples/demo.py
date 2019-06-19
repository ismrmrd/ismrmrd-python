import ismrmrd

acq = ismrmrd.Acquisition()
acq.version = 42
print(acq.version)

img = ismrmrd.Image()

f = ismrmrd.Dataset('./testdata.h5', '/dataset', True)
print( f._file)
# xml = f.readHeader()
