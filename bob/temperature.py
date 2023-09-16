import numpy as np
from bob.constants import kB, protonMass, gamma
from bob.field import Field
from bob.basicField import BasicField
from bob.snapshot import Snapshot
from bob.subsweepSnapshot import SubsweepSnapshot
import astropy.units as pq


class Temperature(Field):
    def getData(self, snapshot: Snapshot) -> np.ndarray:
        if type(snapshot) == SubsweepSnapshot:
            return BasicField("Temperature").getData(snapshot)

        density = BasicField("Density").getData(snapshot)
        if snapshot.sim.params["SGCHEM"]:
            x0He = 0.1
            yn = density / ((1.0 + 4.0 * x0He) * protonMass)
            en = BasicField("InternalEnergy").getData(snapshot) * density
            xH2 = BasicField("ChemicalAbundances", 0).getData(snapshot)
            xHP = BasicField("ChemicalAbundances", 1).getData(snapshot)
            yntot = (1.0 + x0He - xH2 + xHP) * yn
            mu = 1.0 / yntot
        else:
            print("TNG style snapshot, using ElectronAbundance")
            en = BasicField("InternalEnergy").getData(snapshot)
            xe = BasicField("ElectronAbundance").getData(snapshot)
            xH = 0.76
            mu = 4.0 / (1 + 3 * xH + 4 * xH * xe) * protonMass
        temperature = ((gamma - 1.0) * en * mu / kB).decompose()
        assert temperature.unit == pq.K
        return temperature

    @property
    def niceName(self) -> str:
        return "Temperature"

    @property
    def symbol(self) -> str:
        return "T"

    @property
    def unit(self) -> pq.Quantity:
        return pq.K
