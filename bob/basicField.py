from typing import Optional, Dict
import astropy.units as pq
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
            "SGCHEM_HeatCoolRates": "SGCHEM_HeatCoolRates",
            "PhotonFlux": "Flux",
            "Density": "Density",
            "PhotonRates": "PhotonRate",
            "Masses": "Mass",
            "Coordinates": "Coordinates",
        }
        if self.index is None:
            return fieldName[self.name]
        return fieldName[self.name] + str(self.index)

    @property
    def symbol(self) -> str:
        fieldName: Dict[str, str] = {
            "SGCHEM_HeatCoolRates": "SGCHEM_HeatCoolRates",
            "ChemicalAbundances": "Abundance",
            "PhotonFlux": "Flux",
            "Density": "$\rho$",
            "PhotonRates": "PhotonRate",
            "Masses": "$m$",
            "Coordinates": "Coordinates",
        }
        if self.index is None:
            return fieldName[self.name]
        return fieldName[self.name] + str(self.index)

    @property
    def unit(self) -> pq.Quantity:
        if self.name == "Density":
            return pq.g / pq.cm**3
        return 1

    def getData(self, snapshot: "Snapshot") -> np.ndarray:
        if self.name == "Density":
            unit = snapshot.massUnit / (snapshot.lengthUnit**3)
        else:
            unit = 1
        fieldData = readIntoNumpyArray(snapshot.hdf5File["PartType0"][self.name]) * unit
        if self.index is None:
            return fieldData
        else:
            return fieldData[:, self.index]


def readIntoNumpyArray(hdf5Field: h5py._hl.dataset.Dataset) -> np.ndarray:
    fieldH = hdf5Field
    field = np.zeros(fieldH.shape)
    fieldH.read_direct(field)
    return field
