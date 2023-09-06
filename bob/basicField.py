from typing import Optional, Dict, Any
import astropy.units as pq
import astropy.cosmology.units as cu
import h5py
from typing import TYPE_CHECKING
import numpy as np

if TYPE_CHECKING:
    from bob.snapshot import Snapshot
    from bob.baseSnapshot import AnySnap

from bob.field import Field


class DatasetUnavailableError(Exception):
    def __init__(self, s: str) -> None:
        self.message = s

    def __repr__(self) -> str:
        return f"DatasetUnaviableError: {self.message}"


class BasicField(Field):
    def __init__(self, name: str, index: Optional[int] = None, comoving: bool = False, partType: int = 0) -> None:
        self.name = name
        self.index = index
        self.comoving = comoving
        self.partType = partType

    def __repr__(self) -> str:
        if self.index is not None:
            return "{}, {}".format(self.name, self.index)
        else:
            return "{}".format(self.name)

    @property
    def niceName(self) -> str:
        if self.index is None:
            return self.name
        return self.name + str(self.index)

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
            unit *= cu.littleh ** attrs["h_scaling"]
        else:
            unit *= cu.littleh ** attrs["h_scaling"]
        unit *= attrs["to_cgs"]
        return unit

    def getDataForArepoSnapshot(self, snapshot: "Snapshot", indices: Optional[Any] = None) -> pq.Quantity:
        partTypeKey = f"PartType{self.partType}"
        files = snapshot.hdf5FilesWithDataset(partTypeKey)
        if len(files) == 0:
            raise DatasetUnavailableError(f"Dataset {self.partType}/{self.name} not available in snapshot {snapshot}")
        try:
            unit = self.getArbitraryUnit(snapshot, files[0][partTypeKey][self.name])
        except KeyError:
            if self.name == "ChemicalAbundances":
                unit = pq.dimensionless_unscaled
            elif self.name == "IonizationTime":
                unit = snapshot.timeUnit
            elif self.name == "PhotonRates":
                unit = 1 / snapshot.timeUnit
            elif self.name == "PhotonFlux":
                unit = 1 / snapshot.timeUnit
            elif self.name == "Masses":
                unit = pq.g * snapshot.sim.params["UnitMass_in_g"]
            else:
                raise ValueError("Fix units for field: {}".format(self.name))
        if indices is None:
            indices = ...
        fieldData = np.concatenate(list(f[f"PartType{self.partType}"][self.name][...] * unit for f in files))
        if self.index is None:
            return fieldData[indices]
        else:
            return fieldData[indices, self.index]

    def getDataForRaxiomSnapshot(self, snapshot: "Snapshot", indices: Optional[Any] = None) -> pq.Quantity:
        name = self.name.lower()
        if name == "ionized_hydrogen_fraction":
            return snapshot.ionized_hydrogen_fraction()
        elif name == "density":
            return snapshot.density()
        elif name == "coordinates":
            return snapshot.coordinates
        elif name == "chemicalabundances":
            return snapshot.ionized_hydrogen_fraction()
        elif name == "temperature":
            return snapshot.temperature()
        elif name == "heating_rate":
            return snapshot.heating_rate()
        elif name == "timestep":
            return snapshot.timestep()
        elif name == "ionization_time":
            return snapshot.ionization_time()
        elif name == "photon_rate":
            return snapshot.photon_rate()
        elif name == "source":
            return snapshot.source()
        else:
            raise NotImplementedError(f"Field {name}")

    def getData(self, snapshot: "AnySnap", indices: Optional[Any] = None) -> pq.Quantity:
        from bob.snapshot import Snapshot

        if type(snapshot) == Snapshot:
            return self.getDataForArepoSnapshot(snapshot, indices)
        else:
            return self.getDataForRaxiomSnapshot(snapshot, indices)
