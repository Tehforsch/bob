import numpy as np
import h5py


class Snapshot:
    def __init__(self, filename):
        self.filename = filename
        self.coordinates = self.getField("Coordinates")

    def getField(self, field, fieldIndex=None):
        with h5py.File(self.filename, "r") as f:
            field = readIntoNumpyArray(f["PartType0"][field])
        if fieldIndex is None:
            return field
        else:
            return field[:, fieldIndex]

    def __repr__(self):
        return self.filename


def readIntoNumpyArray(hdf5Field):
    fieldH = hdf5Field
    field = np.zeros(fieldH.shape)
    fieldH.read_direct(field)
    return field
