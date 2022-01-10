import numpy as np
from bob.constants import kB, protonMass, gamma
from bob.field import Field
from bob.basicField import BasicField
from bob.snapshot import Snapshot


class Temperature(Field):
    def getData(self, snapshot: Snapshot) -> np.ndarray:
        # The follwoing seems to be wrong
        # inten = self.sf[pt]['InternalEnergy'][:]
        # utherm = inten[ids] * self.sf['Header'].attrs['UnitVelocity_in_cm_per_s']**2
        # return ( calcGamma() - 1. ) * utherm * (calcMu() * apy.const.m_p) / apy.const.k_B

        # The following calculation was taken from voronoi_makeimage.c line 2240
        # and gives the same temperatures as are shown on the Arepo images
        # self.new["density"] = self.new["mass"] / self.new["length"] ** 3
        dens = BasicField("Density").getData(snapshot)
        x0He = 0.1  # REALLY not sure about this one, taken from sgchem def given that CHEMISTRYNETWORK != 1
        yn = dens * snapshot.dens_prev / ((1.0 + 4.0 * x0He) * protonMass)
        en = BasicField("InternalEnergy").getData(snapshot) * dens * snapshot.energyUnit / snapshot.volumeUnit
        xH2 = BasicField("ChemicalAbundances", 0).getData(snapshot)
        xHP = BasicField("ChemicalAbundances", 1).getData(snapshot)
        xHEP = BasicField("ChemicalAbundances", 4).getData(snapshot)
        xHEPP = BasicField("ChemicalAbundances", 5).getData(snapshot)
        yntot = (1.0 + x0He - xH2 + xHP + xHEP + xHEPP) * yn
        print((1.0 + x0He - xH2 + xHP + xHEP + xHEPP))
        print(gamma, en, yntot, protonMass)
        return ((gamma - 1.0) * en / (yntot * kB)).simplified

    @property
    def niceName(self) -> str:
        return "Temperature"
