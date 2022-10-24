from bob.field import Field
from bob.basicField import BasicField
from bob.snapshot import Snapshot
from bob.simulation import Simulation

import numpy as np
import astropy.units as pq
from scipy.spatial import cKDTree


class SourceField(Field):
    def __init__(self, sim: Simulation) -> None:
        self.type_ = sim.params["SX_SOURCES"]

    def getData(self, snapshot: Snapshot) -> np.ndarray:
        if self.type_ == 4:
            coords = BasicField("Coordinates", partType=0).getData(snapshot)
            starMasses = BasicField("masses", partType=4).getData(snapshot)
            starCoords = BasicField("Coordinates", partType=4).getData(snapshot)
            tree = cKDTree(coords)
            cellIndices = tree.query(starCoords)[1]
            source = np.zeros(coords.shape)
            print("Using ridiculous approximation for source strength")
            source[cellIndices] = 1e40 / pq.s * starMasses.to_value(pq.Msun)
            return source
        else:
            raise NotImplementedError("currently, source field is only implemented for star particles")

    @property
    def niceName(self) -> str:
        return "Sources"

    @property
    def symbol(self) -> str:
        return "Sources"

    @property
    def unit(self) -> pq.Quantity:
        return 1.0 / pq.s
