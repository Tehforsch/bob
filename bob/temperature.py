import numpy as np
from bob.constants import kB, protonMass, gamma
from bob.field import Field
from bob.basicField import BasicField
from bob.snapshot import Snapshot
import astropy.units as pq


class Temperature(Field):
    def getData(self, snapshot: Snapshot) -> np.ndarray:
        densityUnit = snapshot.massUnit / (snapshot.lengthUnit**3)
        numberDensityUnit = 1 / (snapshot.lengthUnit**3)
        density = BasicField("Density").getData(snapshot)
        try:
            x0He = 0.1
            yn = density * densityUnit / ((1.0 + 4.0 * x0He) * protonMass)
            en = BasicField("InternalEnergy").getData(snapshot) * density * numberDensityUnit * snapshot.energyUnit
            xH2 = BasicField("ChemicalAbundances", 0).getData(snapshot)
            xHP = BasicField("ChemicalAbundances", 1).getData(snapshot)
            yntot = (1.0 + x0He - xH2 + xHP) * yn
            print("energy snap", np.mean(BasicField("InternalEnergy").getData(snapshot)))
            mu = 1.0 / yntot
        except:
            print("TNG style snapshot, using ElectronAbundance")
            en = BasicField("InternalEnergy").getData(snapshot) * snapshot.velocityUnit**2
            print("energy snap", np.mean(BasicField("InternalEnergy").getData(snapshot)))
            xe = BasicField("ElectronAbundance").getData(snapshot)
            xH = 0.76
            mu = 4.0 / (1 + 3 * xH + 4 * xH * xe) * protonMass
        temperature = ((gamma - 1.0) * en * mu / kB).decompose()
        return temperature.value

    @property
    def niceName(self) -> str:
        return "Temperature"

    @property
    def symbol(self) -> str:
        return "T"

    @property
    def unit(self) -> pq.Quantity:
        return pq.K
