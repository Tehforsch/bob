import numpy as np
from bob.field import Field
from bob.basicField import BasicField
from bob.snapshot import Snapshot
import astropy.units as pq


class ElectronAbundance(Field):
    def getData(self, snapshot: Snapshot) -> np.ndarray:
        try:
            xHP = BasicField("ChemicalAbundances", 1).getData(snapshot)
            electronAbundance = xHP
        except ValueError as e:
            print(e)
            print("TNG style snapshot, using ElectronAbundance")
            electronAbundance = BasicField("ElectronAbundance").getData(snapshot)
        return electronAbundance

    @property
    def niceName(self) -> str:
        return "Temperature"

    @property
    def symbol(self) -> str:
        return "T"

    @property
    def unit(self) -> pq.Quantity:
        return 1
