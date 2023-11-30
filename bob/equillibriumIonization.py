import numpy as np
from bob.field import Field
from bob.basicField import BasicField
from bob.snapshot import Snapshot
from bob.subsweepSnapshot import SubsweepSnapshot
import astropy.units as pq


class EquillibriumIonization(Field):
    def getData(self, snapshot: Snapshot) -> np.ndarray:
        if type(snapshot) == SubsweepSnapshot:
            recomb = BasicField("recombination_rate").getData(snapshot)
            coll_ion = BasicField("collisional_ionization_rate").getData(snapshot)
            return 1.0 - recomb / (recomb + coll_ion)
        raise NotImplementedError

    @property
    def niceName(self) -> str:
        return "equillibrium_ionization"

    @property
    def symbol(self) -> str:
        return "xHII_{eq}"

    @property
    def unit(self) -> pq.Quantity:
        return pq.dimensionless_unscaled
