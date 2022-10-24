from bob.field import Field
from bob.basicField import BasicField
from bob.snapshot import Snapshot
from bob.simulation import Simulation

import numpy as np
import astropy.units as pq
from scipy.spatial import cKDTree


class SourceField(Field):
    def __init__(self, sim: Simulation) -> None:
        self.sim = sim
        self.type_ = sim.params["SX_SOURCES"]

    def getData(self, snapshot: Snapshot) -> np.ndarray:
        coords = BasicField("Coordinates", partType=0).getData(snapshot)
        tree = cKDTree(coords)
        source = np.zeros(coords.shape[0]) / pq.s
        if self.type_ == 4:
            starMasses = BasicField("masses", partType=4).getData(snapshot)
            starCoords = BasicField("Coordinates", partType=4).getData(snapshot)
            cellIndices = tree.query(starCoords)[1]
            print("Using ridiculous approximation for source strength")
            source[cellIndices] = 1e40 / pq.s * starMasses.to_value(pq.Msun)
        elif self.type_ == 10:
            sources = self.sim.sources()
            starCoords = sources.getCoords(self.sim)
            cellIndices = tree.query(starCoords)[1]
            luminosity = sources.get136IonisationRate(self.sim)
            source[cellIndices] = luminosity
        else:
            raise NotImplementedError("currently, source field is only implemented for star particles")
        return source

    @property
    def niceName(self) -> str:
        return "Sources"

    @property
    def symbol(self) -> str:
        return "Sources"

    @property
    def unit(self) -> pq.Quantity:
        return 1.0 / pq.s
