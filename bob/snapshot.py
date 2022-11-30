import os
from typing import Union, Tuple, TYPE_CHECKING, Dict, Any, Callable
from pathlib import Path
import numpy as np
import h5py
import re
import astropy.units as pq
from bob.basicField import BasicField
from bob.timeUtils import TimeQuantity

if TYPE_CHECKING:
    from bob.simulation import Simulation


class SnapNumber:
    def __init__(self, value: Union[int, Tuple[int, int]]):
        self.value = value


class Snapshot:
    def __init__(self, sim: "Simulation", path: Path) -> None:
        self.path = path
        if path.is_dir():
            self.filenames = [path / f for f in os.listdir(path)]
        else:
            self.filenames = [path]
        self.name = self.getName()
        self.sim = sim
        if "subbox" in self.name:
            numbers = self.name.replace("subbox", "").split("_")
            self.number: SnapNumber = SnapNumber((int(numbers[0]), int(numbers[1])))
            self.minExtent, self.maxExtent = sim.subboxCoords()
            self.center = (self.maxExtent + self.minExtent) * 0.5
        else:
            try:
                self.number = SnapNumber(int(self.name))
            except ValueError:
                self.number = SnapNumber(-1)
            self.minExtent = np.array([0.0, 0.0, 0.0]) * self.lengthUnit
            self.maxExtent = np.array([1.0, 1.0, 1.0]) * sim.params["BoxSize"] * self.lengthUnit
            self.center = (self.maxExtent + self.minExtent) * 0.5

    @property
    def hdf5Files(self) -> list[h5py.File]:
        try:
            return [h5py.File(f, "r") for f in self.filenames]
        except OSError:
            print(f"Failed to open snapshot: {self.path}")
            raise

    def filterHdf5Files(self, predicate: Callable[[h5py.File], bool]) -> list[h5py.File]:
        return [f for f in self.hdf5Files if predicate(f)]

    def hdf5FilesWithDataset(self, dataset: str) -> list[h5py.File]:
        return self.filterHdf5Files(lambda f: dataset in f)

    def getName(self) -> str:
        if self.path.is_dir():
            m = re.match("snapdir_(.*)", self.path.name)
            if m is None:
                raise ValueError("Format of snapshot folder does not match expected format snapdir_...")
            return m.groups()[0]
        else:
            m = re.match("snap_(.*).hdf5", self.path.name)
            if m is None:
                return self.path.name.replace(".hdf5", "")
            else:
                return m.groups()[0]

    @property  # type: ignore
    def coordinates(self) -> pq.Quantity:
        return BasicField("Coordinates", comoving=True).getData(self)

    def __repr__(self) -> str:
        return str(self.path)

    @property
    def h(self) -> pq.Quantity:
        return self.sim.params["HubbleParam"]

    @property
    def H0(self) -> pq.Quantity:
        return self.sim.params["HubbleParam"] * 100 * pq.km / pq.s / pq.Mpc

    @property
    def lengthUnit(self) -> pq.Quantity:
        return self.sim.params["UnitLength_in_cm"] * pq.cm

    @property
    def massUnit(self) -> pq.Quantity:
        return self.sim.params["UnitMass_in_g"] * pq.g

    @property
    def velocityUnit(self) -> pq.Quantity:
        return self.sim.params["UnitVelocity_in_cm_per_s"] * pq.cm / pq.s

    @property
    def timeUnit(self) -> pq.Quantity:
        if not self.sim.simType().is_cosmological():
            return self.lengthUnit / self.velocityUnit
        else:
            return pq.dimensionless_unscaled

    @property
    def energyUnit(self) -> pq.Quantity:
        return self.lengthUnit**2 / (self.timeUnit**2) * self.massUnit

    @property
    def scale_factor(self) -> float:
        return self.hdf5Files[0]["Header"].attrs["Time"]

    @property
    def time(self) -> pq.Quantity:
        return self.hdf5Files[0]["Header"].attrs["Time"] * self.timeUnit

    def timeQuantity(self, quantity: str) -> pq.Quantity:
        time = TimeQuantity(self.sim, self.scale_factor * self.timeUnit)
        if quantity == "z":
            # I am completely lost on why but I get two different "redshift" units here that are incopatible and are causing problems, so I'll just take the value and multiply by dimensionless. I find this horrible but I dont know what else to do
            return time.redshift()
        elif quantity == "t":
            return time.time()
        else:
            raise NotImplementedError

    @property
    def attrs(self) -> Dict[str, Any]:
        return self.hdf5Files[0]["Header"].attrs
