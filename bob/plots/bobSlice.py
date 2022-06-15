import argparse

from typing import Tuple
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from scipy.spatial import cKDTree
import numpy as np
import astropy.units as pq

from bob.simulation import Simulation
from bob.snapshot import Snapshot
from bob import config
from bob.postprocessingFunctions import SnapFn, addToList
from bob.result import Result
from bob.allFields import allFields, getFieldByName
from bob.field import Field


def getDataAtPoints(field: Field, snapshot: Snapshot, points: np.ndarray) -> np.ndarray:
    tree = cKDTree(snapshot.coordinates.to(snapshot.lengthUnit).value)
    cellIndices = tree.query(points.to(snapshot.lengthUnit))[1]
    data = field.getData(snapshot)
    return data[cellIndices]


def getSlice(field: Field, snapshot: Snapshot, axisName: str) -> Tuple[Tuple[float, float, float, float], pq.Quantity]:
    axis = getAxisByName(axisName)
    axis = np.array(axis)
    center = snapshot.center
    ortho1, ortho2 = findOrthogonalAxes(axis)
    min1 = np.dot(ortho1, snapshot.minExtent)
    min2 = np.dot(ortho2, snapshot.minExtent)
    max1 = np.dot(ortho1, snapshot.maxExtent)
    max2 = np.dot(ortho2, snapshot.maxExtent)
    n1 = config.dpi * 1
    n2 = config.dpi * 1
    p1, p2 = np.meshgrid(np.linspace(min1, max1, n1), np.linspace(min2, max2, n2))
    coordinates = axis * (center * axis) + np.outer(p1, ortho1) + np.outer(p2, ortho2)
    data = getDataAtPoints(field, snapshot, coordinates)
    return (min1, max1, min2, max2), data.reshape((n1, n2))


class VoronoiSlice(SnapFn):
    def post(self, args: argparse.Namespace, sim: Simulation, snap: Snapshot) -> Result:
        self.axis = args.axis
        field = getFieldByName(args.field)
        result = Result()
        (self.extent, result.data) = getSlice(field, snap, args.axis)
        print(f"Field: {field.niceName}: min: {np.min(result.data):.2e}, mean: {np.mean(result.data):.2e}, max: {np.max(result.data):.2e}")
        return result

    def plot(self, plt: plt.axes, result: Result) -> None:
        xAxis, yAxis = getOtherAxes(self.axis)
        self.style.setDefault("xLabel", f"${xAxis} [UNIT]$")
        self.style.setDefault("yLabel", f"${yAxis} [UNIT]$")
        self.style.setDefault("cLabel", "")
        self.style.setDefault("xUnit", pq.Mpc)
        self.style.setDefault("yUnit", pq.Mpc)
        self.style.setDefault("vUnit", pq.dimensionless_unscaled)
        self.style.setDefault("vLim", (1e-6, 1e0))
        self.setupLabels()
        vmin, vmax = self.style["vLim"]
        self.image(result.data, self.extent, norm=colors.LogNorm(vmin=vmin, vmax=vmax), origin="lower", cmap="Reds")

    def setArgs(self, subparser: argparse.ArgumentParser) -> None:
        super().setArgs(subparser)
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


def getOtherAxes(axis: str) -> Tuple[str, str]:
    if axis == "x":
        return "y", "z"
    elif axis == "y":
        return "x", "z"
    elif axis == "z":
        return "x", "y"
    else:
        raise ValueError(f"Invalid axis: {axis}")


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
