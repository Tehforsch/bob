from scipy.spatial import cKDTree
import astropy.cosmology.units as cu
import astropy.units as pq
import numpy as np

from bob.plotConfig import PlotConfig
from bob.snapshot import Snapshot
from bob.basicField import BasicField
from bob.plots.overHaloMass import OverHaloMass
from bob.constants import protonMass, sigmaH136Bin
from bob.ray import integrateWithRandomRays


class ResolvedEscapeFraction(OverHaloMass):
    def __init__(self, config: PlotConfig) -> None:
        config.setDefault("yUnit", 1.0 * pq.dimensionless_unscaled)
        config.setDefault("yLabel", "$\\tau$")
        config.setDefault("numRays", 10)
        config.setDefault("numPointsAlongRay", 10)
        super().__init__(config)

    def quantity(self, snap: Snapshot) -> pq.Quantity:
        density = BasicField("Density").getData(snap).to(pq.g / pq.cm**3, cu.with_H0(snap.H0))
        xHP = BasicField("ChemicalAbundances", 1).getData(snap)
        n = density / protonMass
        sigma = (1.0 - xHP) * sigmaH136Bin
        return n * sigma

    def evaluateQuantityForHalo(self, tree: cKDTree, quantity: pq.Quantity, pos: pq.Quantity, r: pq.Quantity) -> pq.Quantity:
        return np.mean(integrateWithRandomRays(tree, quantity, pos, r, self.config["numRays"], self.config["numPointsAlongRay"]))
