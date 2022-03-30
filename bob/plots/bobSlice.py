import argparse

from typing import Tuple
import matplotlib.pyplot as plt
from scipy.spatial import cKDTree
import numpy as np

from bob.simulation import Simulation
from bob.snapshot import Snapshot
from bob import config
from bob.postprocessingFunctions import SnapFn, addToList
from bob.result import Result
from bob.allFields import allFields, getFieldByName


class VoronoiSlice(SnapFn):
    def post(self, args: argparse.Namespace, sim: Simulation, snap: Snapshot) -> Result:
        axis = getAxisByName(args.axis)
        field = getFieldByName(args.field)
        axis = np.array(axis)
        center = snap.center
        self.ortho1, self.ortho2 = findOrthogonalAxes(axis)
        self.min1 = np.dot(self.ortho1, snap.minExtent)
        self.min2 = np.dot(self.ortho2, snap.minExtent)
        self.max1 = np.dot(self.ortho1, snap.maxExtent)
        self.max2 = np.dot(self.ortho2, snap.maxExtent)
        n1 = config.dpi * 3
        n2 = config.dpi * 3
        p1, p2 = np.meshgrid(np.linspace(self.min1, self.max1, n1), np.linspace(self.min2, self.max2, n2))
        coordinates = axis * (center * axis) + np.outer(p1, self.ortho1) + np.outer(p2, self.ortho2)
        tree = cKDTree(snap.coordinates)
        cellIndices = tree.query(coordinates)[1]
        cellIndices = cellIndices.reshape((n1, n2))
        data = field.getData(snap)
        print(f"Field: {field.niceName}: min: {np.min(data):.2e}, mean: {np.mean(data):.2e}, max: {np.max(data):.2e}")
        return Result([data[cellIndices]])

    def plot(self, plt: plt.axes, result: Result) -> None:
        plt.xlabel(getAxisName(self.ortho1))
        plt.ylabel(getAxisName(self.ortho2))
        extent = (self.min1, self.max1, self.min2, self.max2)
        plt.imshow(result.arrs[0], extent=extent, origin="lower", cmap="Reds")
        plt.colorbar()

    def setArgs(self, subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument("--axis", required=True, choices=["x", "y", "z"])
        subparser.add_argument("--field", required=True, choices=[f.niceName for f in allFields])

    def getName(self, args: argparse.Namespace) -> str:
        return f"{self.name}_{args.axis}_{args.field}"


def getAxisByName(name: str) -> np.ndarray:
    return [np.array([1.0, 0.0, 0.0]), np.array([0.0, 1.0, 0.0]), np.array([0.0, 0.0, 1.0])][["x", "y", "z"].index(name)]


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


addToList("slice", VoronoiSlice())
