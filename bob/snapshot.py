from typing import Union, Tuple, TYPE_CHECKING, Dict, Any
from pathlib import Path
import numpy as np
import h5py
import re
import astropy.units as pq
from bob.basicField import BasicField

if TYPE_CHECKING:
    from bob.simulation import Simulation


class SnapNumber:
    def __init__(self, value: Union[int, Tuple[int, int]]):
        self.value = value


class Snapshot:
    def __init__(self, sim: "Simulation", filename: Path) -> None:
        self.filename = filename
        self.name = self.getName()
        if "subbox" in self.name:
            numbers = self.name.replace("subbox", "").split("_")
            self.number: SnapNumber = SnapNumber((int(numbers[0]), int(numbers[1])))
            self.minExtent, self.maxExtent = sim.subboxCoords()
            self.center = (self.maxExtent + self.minExtent) * 0.5
        else:
            self.number = SnapNumber(int(self.name))
            self.minExtent = np.array([0.0, 0.0, 0.0]) * self.lengthUnit
            self.maxExtent = np.array([1.0, 1.0, 1.0]) * sim.params["BoxSize"] * self.lengthUnit
            self.center = (self.maxExtent + self.minExtent) * 0.5

    @property
    def hdf5File(self) -> h5py.File:
        return h5py.File(self.filename, "r")

    def hasField(self, field: str) -> bool:
        return field in self.hdf5File["PartType0"]

    def getName(self) -> str:
        match = re.match("snap_(.*).hdf5", self.filename.name)
        if match is None:
            raise ValueError("Wrong snapshot filename")
        else:
            return match.groups()[0]

    @property  # type: ignore
    def coordinates(self) -> pq.Quantity:
        return BasicField("Coordinates", comoving=True).getData(self)

    def __repr__(self) -> str:
        return str(self.filename)

    @property
    def h(self) -> pq.Quantity:
        return self.hdf5File["Header"].attrs["HubbleParam"]

    @property
    def lengthUnit(self) -> pq.Quantity:
        return self.hdf5File["Header"].attrs["UnitLength_in_cm"] * pq.cm

    @property
    def massUnit(self) -> pq.Quantity:
        return self.hdf5File["Header"].attrs["UnitMass_in_g"] * pq.g

    @property
    def velocityUnit(self) -> pq.Quantity:
        return self.hdf5File["Header"].attrs["UnitVelocity_in_cm_per_s"] * pq.cm / pq.s

    @property
    def timeUnit(self) -> pq.Quantity:
        return self.lengthUnit / self.velocityUnit

    @property
    def energyUnit(self) -> pq.Quantity:
        return self.lengthUnit**2 / (self.timeUnit**2) * self.massUnit

    @property
    def scale_factor(self) -> float:
        return self.hdf5File["Header"].attrs["Time"]

    @property
    def time(self) -> pq.Quantity:
        return self.hdf5File["Header"].attrs["Time"] * self.timeUnit

    @property
    def attrs(self) -> Dict[str, Any]:
        return self.hdf5File["Header"].attrs
