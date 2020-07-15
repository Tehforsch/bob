from pathlib import Path
import numpy as np
import h5py
from bob.field import Field


class Snapshot:
    def __init__(self, filename: Path) -> None:
        self.filename = filename
        self.coordinates = self.getField(Field("Coordinates"))

    def getField(self, field: Field) -> np.ndarray:
        with h5py.File(self.filename, "r") as f:
            fieldData = readIntoNumpyArray(f["PartType0"][field.name])
        if field.index is None:
            return fieldData
        else:
            return fieldData[:, field.index]

    def __repr__(self) -> str:
        return str(self.filename)


def readIntoNumpyArray(hdf5Field: h5py._hl.dataset.Dataset) -> np.ndarray:
    fieldH = hdf5Field
    field = np.zeros(fieldH.shape)
    fieldH.read_direct(field)
    return field
