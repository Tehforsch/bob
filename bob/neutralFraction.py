
import numpy as np
from bob.constants import kB, protonMass, gamma
from bob.field import Field
from bob.basicField import BasicField
from bob.snapshot import Snapshot
from bob.subsweepSnapshot import SubsweepSnapshot
import astropy.units as pq


class NeutralFraction(Field):
    def getData(self, snapshot: Snapshot) -> np.ndarray:
        return 1.0 - BasicField("ionized_hydrogen_fraction").getData(snapshot)

    @property
    def niceName(self) -> str:
        return "neutral_hydrogen_fraction"

    @property
    def symbol(self) -> str:
        return "$x_{\\mathrm{HI}}$"

    @property
    def unit(self) -> pq.Quantity:
        return pq.dimensionless_unscaled
