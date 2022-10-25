import numpy as np
from bob.field import Field
from bob.basicField import BasicField
from bob.snapshot import Snapshot
import astropy.units as pq


class Volume(Field):
    def __init__(self, comoving: bool = False) -> None:
        self.comoving = comoving

    def getData(self, snapshot: Snapshot) -> np.ndarray:
        density = BasicField("Density").getData(snapshot)
        masses = BasicField("Masses").getData(snapshot)
        return masses / density

    @property
    def niceName(self) -> str:
        return "Volume"

    @property
    def symbol(self) -> str:
        return "V"

    @property
    def unit(self) -> pq.Quantity:
        if self.comoving:
            return pq.cm**3 / pq.h**3
        else:
            return pq.cm**3
