from typing import Optional, Dict
import astropy.units as pq
import h5py
import numpy as np

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bob.snapshot import Snapshot

from bob.field import Field


class BasicField(Field):
    def __init__(self, name: str, index: Optional[int] = None, comoving: bool = False) -> None:
        self.name = name
        self.index = index
        self.comoving = comoving

    def __repr__(self) -> str:
        if self.index is not None:
            return "{}, {}".format(self.name, self.index)
        else:
            return "{}".format(self.name)

    @property
    def niceName(self) -> str:
        fieldName: Dict[str, str] = {
            "SGCHEM_HeatCoolRates": "SGCHEM_HeatCoolRates",
            "InternalEnergy": "InternalEnergy",
            "ChemicalAbundances": "Abundance",
            "PhotonFlux": "PhotonFlux",
            "Density": "Density",
            "PhotonRates": "PhotonRates",
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
            "InternalEnergy": "InternalEnergy",
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
        if self.name == "InternalEnergy":
            return pq.cm**2 / pq.s**2
        else:
            return 1

    def getArbitraryUnit(self, snapshot: "Snapshot", dataset: h5py.Dataset) -> pq.Quantity:
        attrs = dataset.attrs
        unit = pq.cm ** attrs["length_scaling"]
        unit *= pq.g ** attrs["mass_scaling"]
        unit *= (pq.cm / pq.s) ** attrs["velocity_scaling"]
        if not self.comoving:
            unit *= snapshot.h ** attrs["h_scaling"]
            unit *= snapshot.scale_factor ** attrs["a_scaling"]
        unit *= attrs["to_cgs"]
        return unit

    def getData(self, snapshot: "Snapshot") -> np.ndarray:
        try:
            unit = self.getArbitraryUnit(snapshot, snapshot.hdf5File["PartType0"][self.name])
        except KeyError:
            if self.name == "ChemicalAbundances":
                unit = pq.dimensionless_unscaled
            elif self.name == "IonizationTime":
                unit = snapshot.timeUnit
            elif self.name == "PhotonRates":
                unit = 1 / snapshot.timeUnit
            elif self.name == "PhotonFlux":
                unit = 1 / snapshot.timeUnit
            else:
                raise ValueError("Fix units for field: {}".format(self.name))
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
