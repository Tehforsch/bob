from scipy.spatial import cKDTree
import astropy.units as pq
import numpy as np


class Ray:
    def __init__(self, pos: pq.Quantity, direction: pq.Quantity) -> None:
        self.pos = pos
        self.direction = direction

    def integrate(self, tree: cKDTree, dataset: pq.Quantity, interval: tuple[pq.Quantity, pq.Quantity], numValues: int) -> pq.Quantity:
        tValues = np.linspace(interval[0], interval[1], num=numValues)
        positions = self.pos + np.outer(tValues, self.direction)
        cellIndices = tree.query(positions)[1]
        dr = (interval[1] - interval[0]) / numValues
        return np.sum(dataset[cellIndices]) * dr
