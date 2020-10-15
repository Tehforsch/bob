from typing import Optional, Dict, Union
import h5py
import numpy as np

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bob.snapshot import Snapshot

from bob.field import Field


class BasicField(Field):
    def __init__(self, name: str, index: Optional[int] = None) -> None:
        self.name = name
        self.index = index

    def __repr__(self) -> str:
        if self.index is not None:
            return "{}, {}".format(self.name, self.index)
        else:
            return "{}".format(self.name)

    @property
    def niceName(self) -> str:
        fieldName: Dict[str, str] = {
            "ChemicalAbundances": "Abundance",
            "PhotonFlux": "Flux",
            "Density": "Density",
            "PhotonRates": "PhotonRate",
            "Masses": "Mass",
            "Coordinates": "Coordinates",
        }
        if self.index is None:
            return fieldName[self.name]
        return fieldName[self.name] + str(self.index)

    def getData(self, snapshot: "Snapshot") -> np.ndarray:
        fieldData = readIntoNumpyArray(snapshot.hdf5File["PartType0"][self.name])
        if self.index is None:
            return fieldData
        else:
            return fieldData[:, self.index]


def readIntoNumpyArray(hdf5Field: h5py._hl.dataset.Dataset) -> np.ndarray:
    fieldH = hdf5Field
    field = np.zeros(fieldH.shape)
    fieldH.read_direct(field)
    return field
