from typing import Iterable
from scipy.spatial import cKDTree
import astropy.units as pq
import numpy as np


class Ray:
    def __init__(self, pos: pq.Quantity, direction: pq.Quantity) -> None:
        self.pos = pos
        self.direction = direction

    def integrate(self, tree: cKDTree, dataset: pq.Quantity, interval: tuple[pq.Quantity, pq.Quantity], numValues: int) -> pq.Quantity:
        values = self.getValues(tree, dataset, interval, numValues)
        dr = (interval[1] - interval[0]) / numValues
        return np.sum(values) * dr

    def getValues(self, tree: cKDTree, dataset: pq.Quantity, interval: tuple[pq.Quantity, pq.Quantity], numValues: int) -> pq.Quantity:
        tValues = np.linspace(interval[0], interval[1], num=numValues)
        positions = self.pos + np.outer(tValues, self.direction)
        cellIndices = tree.query(positions)[1]
        return dataset[cellIndices]


def getRandomRaysFrom(startPos: pq.Quantity, numRays: int) -> Iterable[Ray]:
    directions = np.random.rand(numRays, 3)
    for i in range(numRays):
        d = directions[i, :] / np.linalg.norm(directions[i, :])
        yield Ray(startPos, d)


def integrateWithRandomRays(
    tree: cKDTree, quantity: pq.Quantity, startPos: pq.Quantity, rayLength: pq.Quantity, numRays: int, numPointsAlongRay: int
) -> pq.Quantity:
    values = np.zeros(numRays) * quantity.unit * rayLength.unit
    for (i, ray) in enumerate(getRandomRaysFrom(startPos, numRays)):
        values[i] = ray.integrate(tree, quantity, (0.0 * rayLength, rayLength), numPointsAlongRay)
    return values
