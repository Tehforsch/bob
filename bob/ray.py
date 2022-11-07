from scipy.spatial import cKDTree
import astropy.units as pq
import numpy as np


class Ray:
    def __init__(self, pos: pq.Quantity, direction: pq.Quantity) -> None:
        self.pos = pos
        self.direction = direction

    def getValues(self, tree: cKDTree, dataset: pq.Quantity, interval: tuple[float, float], numValues: int) -> pq.Quantity:
        tValues = np.linspace(interval[0], interval[1], num=numValues)
        positions = self.pos + tValues * self.direction
        cellIndices = tree.query(positions)[1]
        return dataset[cellIndices]
