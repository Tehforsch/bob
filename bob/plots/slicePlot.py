import argparse

from typing import Any, Dict, Tuple, List
import matplotlib.pyplot as plt
from scipy.spatial import cKDTree
import numpy as np

from bob.simulation import Simulation
from bob.snapshot import Snapshot
from bob.field import Field
from bob import config
from bob.postprocessingFunctions import SnapFn
from bob.result import Result


class VoronoiSlice(SnapFn):
    def post(self, args: argparse.Namespace, sim: Simulation, snap: Snapshot) -> Result:
        print(args)
        axis = np.array(axis)
        center = snap.center
        ortho1, ortho2 = findOrthogonalAxes(axis)
        min1 = np.dot(ortho1, snap.minExtent)
        min2 = np.dot(ortho2, snap.minExtent)
        max1 = np.dot(ortho1, snap.maxExtent)
        max2 = np.dot(ortho2, snap.maxExtent)
        n1 = config.dpi * 3
        n2 = config.dpi * 3
        p1, p2 = np.meshgrid(np.linspace(min1, max1, n1), np.linspace(min2, max2, n2))
        coordinates = axis * (center * axis) + np.outer(p1, ortho1) + np.outer(p2, ortho2)
        tree = cKDTree(snap.coordinates)
        cellIndices = tree.query(coordinates)[1]
        cellIndices = cellIndices.reshape((n1, n2))
        data = field.getData(snap)
        return data[cellIndicies]

    def plot(self, plt: plt.axes, result: Result) -> None:
        print(f"Field: {field.niceName}: min: {np.min(data):.2e}, mean: {np.mean(data):.2e}, max: {np.max(data):.2e}")
        ax.xlabel(getAxisName(ortho1))
        ax.ylabel(getAxisName(ortho2))
        extent = (min1, max1, min2, max2)
        ax.imshow(result.arrs[0], extent=extent, origin="lower", cmap="Reds", **plotSettings)
        plt.colorbar()


def getAxisName(axis: np.ndarray) -> str:
    xAxis = np.array([1.0, 0.0, 0.0])
    yAxis = np.array([0.0, 1.0, 0.0])
    zAxis = np.array([0.0, 0.0, 1.0])
    dotProducts = [np.abs(np.dot(axis, a)) for a in [xAxis, yAxis, zAxis]]
    mostParallel = np.argmax(dotProducts)
    return ["x", "y", "z"][mostParallel]


def getSlice(
    array: np.ndarray,
    coordinates: np.ndarray,
    start: np.ndarray,
    axis: np.ndarray,
    thickness: float,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    indices = np.where(np.abs(np.dot(coordinates - start, axis)) < thickness)
    axis1, axis2 = findOrthogonalAxes(axis)
    return (
        np.dot(coordinates[indices], axis1),
        np.dot(coordinates[indices], axis2),
        array[indices],
    )


def findOrthogonalAxes(axis: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    xAxis = np.array([1.0, 0.0, 0.0])
    yAxis = np.array([0.0, 1.0, 0.0])
    zAxis = np.array([0.0, 0.0, 1.0])
    dotProducts = [np.abs(np.dot(axis, a)) for a in [xAxis, yAxis, zAxis]]
    mostParallel = np.argmax(dotProducts)
    mostOrthogonal = [0, 1, 2]
    mostOrthogonal.remove(int(mostParallel))
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
