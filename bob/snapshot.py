from typing import Union, Tuple, TYPE_CHECKING
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
            self.minExtent = np.array([0.0, 0.0, 0.0])
            self.maxExtent = np.array([1.0, 1.0, 1.0]) * sim.params["BoxSize"]
            self.center = (self.maxExtent + self.minExtent) * 0.5
        self.hdf5File: h5py.File = h5py.File(self.filename, "r")
        self.initConversionFactors()

    def getName(self) -> str:
        match = re.match("snap_(.*).hdf5", self.filename.name)
        if match is None:
            raise ValueError("Wrong snapshot filename")
        else:
            return match.groups()[0]

    @property  # type: ignore
    def coordinates(self) -> np.ndarray:
        return BasicField("Coordinates").getData(self)

    def __repr__(self) -> str:
        return str(self.filename)

    def initConversionFactors(self) -> None:
        self.h = self.hdf5File["Header"].attrs["HubbleParam"]
        self.lengthUnit = self.hdf5File["Header"].attrs["UnitLength_in_cm"] * pq.cm
        self.massUnit = self.hdf5File["Header"].attrs["UnitMass_in_g"] * pq.g
        self.velocityUnit = self.hdf5File["Header"].attrs["UnitVelocity_in_cm_per_s"] * pq.cm / pq.s
        self.timeUnit = self.lengthUnit / self.velocityUnit
        self.energyUnit = self.lengthUnit**2 / (self.timeUnit**2) * self.massUnit
        self.scale_factor = self.hdf5File["Header"].attrs["Time"]
        self.time = self.hdf5File["Header"].attrs["Time"] * self.timeUnit
