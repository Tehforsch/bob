from typing import Union
import astropy.units as pq
import h5py

from bob.timeUtils import TimeQuantity

AnySnap = Union["Snapshot", "SubsweepSnapshot"]


class BaseSnapshot:
    def __init__(self) -> None:
        self.sim = None
        self.time = None

    def timeQuantity(self, quantity: str) -> pq.Quantity:
        time = TimeQuantity(self.sim, self.time)
        if quantity == "z":
            # I am completely lost on why but I get two different "redshift" units here that are incopatible and are causing problems, so I'll just take the value and multiply by dimensionless. I find this horrible but I dont know what else to do
            return time.redshift()
        elif quantity == "t":
            return time.time()
        else:
            raise ValueError(f"Unkown time quantity: {quantity}")

    @property
    def hdf5Files(self) -> list[h5py.File]:
        try:
            return [h5py.File(f, "r") for f in self.filenames]
        except OSError:
            print(f"Failed to open snapshot: {self.path}")
            raise
