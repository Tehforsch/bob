from scipy.spatial import cKDTree
import astropy.cosmology.units as cu
import astropy.units as pq
import numpy as np

from bob.plotConfig import PlotConfig
from bob.snapshot import Snapshot
from bob.basicField import BasicField
from bob.plots.overHaloMass import OverHaloMass
from bob.constants import protonMass, sigmaH136Bin
from bob.ray import Ray
from bob.util import getArrayQuantity


class ResolvedEscapeFraction(OverHaloMass):
    def __init__(self, config: PlotConfig) -> None:
        config.setDefault("yUnit", pq.dimensionless_unscaled)
        config.setDefault("yLabel", "$f_{\\mathrm{esc}}$")
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
        directions = np.random.rand(self.config["numRays"], 3)
        values = []
        for i in range(self.config["numRays"]):
            d = directions[i, :] / np.linalg.norm(directions[i, :])
            ray = Ray(pos, d)
            values.append(ray.integrate(tree, quantity, (0.0 * r, r), self.config["numPointsAlongRay"]))
        return np.mean(getArrayQuantity(values))
