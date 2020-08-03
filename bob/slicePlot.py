from typing import Dict, Any, Tuple
import numpy as np
import matplotlib.pyplot as plt
from bob.snapshot import Snapshot
from bob.field import Field


class Slice:
    def __init__(self, snapshot: Snapshot, field: Field, start: np.array, axis: np.array):
        self.snapshot = snapshot
        self.field = field
        self.start = start
        self.axis = axis / np.linalg.norm(axis)
        self.vmin = 0
        self.vmax = 1
        self.thickness = 0.02

    def plot(self, ax: plt.axes, **plotSettings: Dict[str, Any]) -> None:
        field = self.field.getData(self.snapshot)
        print(np.mean(field), np.max(field))
        coordinates = self.snapshot.coordinates
        coord1, coord2, values = getSlice(field, coordinates, self.start, self.axis, self.thickness)
        ax.scatter(coord1, coord2, c=values, alpha=1.0, **plotSettings, vmin=self.vmin, vmax=self.vmax)


def getSlice(array: np.ndarray, coordinates: np.ndarray, start: np.ndarray, axis: np.ndarray, thickness: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    indices = np.where(np.abs(np.dot(coordinates - start, axis)) < thickness)
    axis1, axis2 = findOrthogonalAxes(axis)
    return np.dot(coordinates[indices], axis1), np.dot(coordinates[indices], axis2), array[indices]


def findOrthogonalAxes(axis: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    xAxis = np.array([1.0, 0.0, 0.0])
    yAxis = np.array([0.0, 1.0, 0.0])
    zAxis = np.array([0.0, 0.0, 1.0])
    dotProducts = [np.abs(np.dot(axis, a)) for a in [xAxis, yAxis, zAxis]]
    mostParallel = np.argmax(dotProducts)
    mostOrthogonal = [0, 1, 2]
    mostOrthogonal.remove(mostParallel)
    basicAxis1 = [xAxis, yAxis, zAxis][mostOrthogonal[0]]
    axis1 = np.cross(basicAxis1, axis)
    axis1 = axis1 / np.linalg.norm(axis)
    axis2 = np.cross(axis1, axis)
    axis2 = axis2 / np.linalg.norm(axis)
    return axis1, axis2
