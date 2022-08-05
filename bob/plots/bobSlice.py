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
from bob.plots.timePlots import getTimeOrRedshift
from bob.plotConfig import PlotConfig


def getDataAtPoints(field: Field, snapshot: Snapshot, points: pq.Quantity) -> np.ndarray:
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
    if len(data.shape) == 1:
        return (min1, max1, min2, max2), data.reshape((n1, n2))
    else:
        return (min1, max1, min2, max2), data.reshape((n1, n2, 3))


class VoronoiSlice(SnapFn):
    def __init__(self, config: PlotConfig) -> None:
        super().__init__(config)
        self.config.setRequired("axis", choices=["x", "y", "z"])
        self.config.setRequired("field", choices=[f.niceName for f in allFields])
        self.field = getFieldByName(self.config["field"])
        xAxis, yAxis = getOtherAxes(config["axis"])
        self.config.setDefault("xLabel", f"${xAxis} [UNIT]$")
        self.config.setDefault("yLabel", f"${yAxis} [UNIT]$")
        self.config.setDefault("cLabel", "")
        self.config.setDefault("xUnit", pq.Mpc)
        self.config.setDefault("yUnit", pq.Mpc)
        self.config.setDefault("vUnit", self.field.unit)
        self.config.setDefault("vLim", (1e-6, 1e0))
        self.config.setDefault("log", True)
        self.config.setDefault("logmin0", -9)
        self.config.setDefault("logmin1", -9)
        self.config.setDefault("logmin2", -9)
        self.config.setDefault("logmax0", 0)
        self.config.setDefault("logmax1", 0)
        self.config.setDefault("logmax2", 0)
        self.config.setDefault("showTime", True)

    def post(self, sim: Simulation, snap: Snapshot) -> Result:
        self.axis = self.config["axis"]
        result = Result()
        result.redshift = getTimeOrRedshift(sim, snap)
        (self.extent, result.data) = getSlice(self.field, snap, self.config["axis"])
        print(f"Field: {self.field.niceName}: min: {np.min(result.data):.2e}, mean: {np.mean(result.data):.2e}, max: {np.max(result.data):.2e}")
        return result

    def transformLog(self, data: pq.Quantity) -> pq.Quantity:
        epsilon = 1e-50
        for i in range(3):
            logmin = self.config[f"logmin{i}"]
            logmax = self.config[f"logmax{i}"]
            log = np.maximum(np.log10(data[:, :, i] + epsilon), logmin)
            data[:, :, i] = (log + (-logmin)) / (logmax - logmin)
        print(np.min(data[:, :, 0]))
        print(np.mean(data[:, :, 0]))
        print(np.max(data[:, :, 0]))
        print(np.min(data[:, :, 1]))
        print(np.mean(data[:, :, 1]))
        print(np.max(data[:, :, 1]))

    def plot(self, plt: plt.axes, result: Result) -> None:
        xAxis, yAxis = getOtherAxes(self.axis)
        self.setupLabels()
        vmin, vmax = self.config["vLim"]
        if result.data.ndim == 3:
            # Combined fields: each entry is a color
            if self.config["log"]:
                self.transformLog(result.data)
        print(f"min: {np.min(result.data)}, max: {np.max(result.data)}")
        if self.config["log"]:
            self.image(result.data, self.extent, norm=colors.LogNorm(vmin=vmin, vmax=vmax), origin="lower", cmap="Reds")
        else:
            self.image(result.data, self.extent, vmin=vmin, vmax=vmax, origin="lower")
        if self.config["showTime"]:
            plt.text(0, 0, f"Redshift: {result.redshift:.01f}", fontsize=12)

    def getName(self) -> str:
        axis = self.config["axis"]
        field = self.config["field"]
        return f"{self.name}_{axis}_{field}"


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
    axes = [axis1, axis2]
    axes.sort(key=lambda coord: (-coord[0], -coord[1], -coord[2]))
    return axes[0], axes[1]


addToList("slice", VoronoiSlice)
