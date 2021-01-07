from typing import Any, Dict, Tuple
import matplotlib.pyplot as plt
from scipy.spatial import cKDTree
import numpy as np

from bob.simulation import Simulation
from bob.snapshot import Snapshot
from bob.field import Field
from bob import config


def voronoiSlice(ax: plt.axes, sim: Simulation, snap: Snapshot, field: Field, center: np.ndarray, axis: np.ndarray, **plotSettings: Dict[str, Any]) -> None:
    axis = np.array(axis)
    center = np.array(center)
    min1 = 0.0
    max1 = sim.params["BoxSize"]
    min2 = 0.0
    max2 = sim.params["BoxSize"]
    ortho1, ortho2 = findOrthogonalAxes(axis)
    n1 = config.dpi * 3
    n2 = config.dpi * 3
    p1, p2 = np.meshgrid(np.linspace(min1, max1, n1), np.linspace(min2, max2, n2))
    coordinates = axis * (center * axis) + np.outer(p1, ortho1) + np.outer(p2, ortho2)
    tree = cKDTree(snap.coordinates)
    cellIndices = tree.query(coordinates)[1]
    cellIndices = cellIndices.reshape((n1, n2))
    # data = np.log(field.getData(snap))
    data = field.getData(snap)
    print(f"Field: {field.niceName}: min: {np.min(data):.2e}, mean: {np.mean(data):.2e}, max: {np.max(data):.2e}")
    ax.xlabel(getAxisName(ortho1))
    ax.ylabel(getAxisName(ortho2))
    extent = (0, sim.params["BoxSize"], 0, sim.params["BoxSize"])
    ax.imshow(data[cellIndices], extent=extent, origin="lower", cmap="Reds", **plotSettings)
    plt.colorbar()


def getAxisName(axis: np.ndarray) -> str:
    xAxis = np.array([1.0, 0.0, 0.0])
    yAxis = np.array([0.0, 1.0, 0.0])
    zAxis = np.array([0.0, 0.0, 1.0])
    dotProducts = [np.abs(np.dot(axis, a)) for a in [xAxis, yAxis, zAxis]]
    mostParallel = np.argmax(dotProducts)
    return ["x", "y", "z"][mostParallel]


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
    if np.sum(axis1) < 0:
        axis1 = -axis1
    if np.sum(axis2) < 0:
        axis2 = -axis2
    return axis1, axis2
