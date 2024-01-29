from typing import Tuple
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from scipy.spatial import cKDTree
import numpy as np
import astropy.units as pq
import astropy.cosmology.units as cu

from bob.simulation import Simulation
from bob.subsweepSimulation import Cosmology
from bob.snapshot import Snapshot
from bob import config
from bob.postprocessingFunctions import SnapFn
from bob.result import Result
from bob.allFields import allFields, getFieldByName
from bob.field import Field
from bob.plotConfig import PlotConfig


def getDefaultCmap(field: str):
    e = {
        "temperature": "Reds",
        "ionized_hydrogen_fraction": "coolwarm",
        "collisional_ionization_rate": "Purples",
        "density": "Greys",
        "equillibrium_neutral_fraction": "Blues",
        "neutral_hydrogen_fraction": "Blues",
        "photoionization_rate": "Oranges",
        "recombination_rate": "autumn",
    }
    field = field.lower()
    if field in e:
        return e[field]
    else:
        print(f"Using default colormap for {field}")
        return "viridis"


def getDataAtPoints(field: Field, snapshot: Snapshot, points: pq.Quantity) -> np.ndarray:
    lengthUnit = snapshot.lengthUnit
    coords = snapshot.coordinates.to(lengthUnit, cu.with_H0(snapshot.H0)).value
    points = points.to(snapshot.lengthUnit, cu.with_H0(snapshot.H0))
    tree = cKDTree(coords)
    cellIndices = tree.query(points)[1]
    data = field.getData(snapshot)
    return data[cellIndices]


def getSlice(field: Field, snapshot: Snapshot, axisName: str, position: float, minExtent=None, maxExtent=None) -> Tuple[Tuple[float, float, float, float], pq.Quantity]:
    axis = getAxisByName(axisName)
    axis = np.array(axis)
    center = (snapshot.maxExtent * axis) * position
    ortho1, ortho2 = findOrthogonalAxes(axis)
    minExtent = snapshot.minExtent if minExtent is None else minExtent
    maxExtent = snapshot.maxExtent if maxExtent is None else maxExtent
    min1 = np.dot(ortho1, minExtent)
    min2 = np.dot(ortho2, minExtent)
    max1 = np.dot(ortho1, maxExtent)
    max2 = np.dot(ortho2, maxExtent)
    n1 = config.dpi * 1
    n2 = config.dpi * 1
    p1, p2 = np.meshgrid(np.linspace(min1, max1, n1), np.linspace(min2, max2, n2))
    coordinates = axis * (center * axis) + np.outer(p1, ortho1) + np.outer(p2, ortho2)
    data = getDataAtPoints(field, snapshot, coordinates)
    if len(data.shape) == 1:
        return (min1, max1, min2, max2), data.reshape((n1, n2))
    else:
        return (min1, max1, min2, max2), data.reshape((n1, n2, 3))


class Slice(SnapFn):
    def __init__(self, config: PlotConfig) -> None:
        super().__init__(config)
        self.config.setDefault("axis", "z", choices=["x", "y", "z"])
        self.config.setDefault("field", "Abundance1", choices=[f.niceName for f in allFields])
        print(self.config["field"])
        self.config.setDefault("colorscale", None)
        xAxis, yAxis = getOtherAxes(config["axis"])
        self.config.setDefault("xLabel", f"${xAxis} [UNIT]$")
        self.config.setDefault("yLabel", f"${yAxis} [UNIT]$")
        self.config.setDefault("cLabel", "{} [${}$]".format(self.field.niceName, str(self.config["vUnit"])))
        self.config.setDefault("vLim", None)
        self.config.setDefault("xUnit", pq.Mpc)
        self.config.setDefault("yUnit", pq.Mpc)
        self.config.setDefault("vUnit", self.field.unit)
        self.config.setDefault("log", True)
        self.config.setDefault("logmin0", -9)
        self.config.setDefault("logmin1", -9)
        self.config.setDefault("logmin2", -9)
        self.config.setDefault("logmax0", 0)
        self.config.setDefault("logmax1", 0)
        self.config.setDefault("logmax2", 0)
        self.config.setDefault("relativePosition", 0.5)
        self.config.setDefault("name", self.name + "_{simName}_{snapName}_{field}_{axis}")

    @property
    def field(self) -> Field:
        return getFieldByName(self.config["field"])

    def post(self, sim: Simulation, snap: Snapshot) -> Result:
        result = super().post(sim, snap)
        (extent, result.data) = getSlice(self.field, snap, self.config["axis"], self.config["relativePosition"])
        result.data = result.data.to(self.config["vUnit"], cu.with_H0(snap.H0))
        result.extent = list(extent)
        print(f"Field: {self.field.niceName}: min: {np.min(result.data):.2e}, mean: {np.mean(result.data):.2e}, max: {np.max(result.data):.2e}")
        result.a = sim.scale_factor()
        result.h = sim.little_h * pq.dimensionless_unscaled
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

    def plotData(self, plt: plt.axes, result: Result, colorbar=True):
        xAxis, yAxis = getOtherAxes(self.config["axis"])
        cosmology = Cosmology({"a": result.a.value, "h": result.h.value})
        if self.config["colorscale"] is None:
            self.config["colorscale"] = getDefaultCmap(self.config["field"])
        with cosmology.unit_context():
            if self.config["vLim"] is not None:
                vmin, vmax = self.config["vLim"]
            else:
                vmin = np.min(result.data).to_value(self.config["vUnit"])
                vmax = np.max(result.data).to_value(self.config["vUnit"])
            if result.data.ndim == 3:
                # Combined fields: each entry is a color
                if self.config["log"]:
                    self.transformLog(result.data)
            print(f"min: {np.min(result.data)}, max: {np.max(result.data)}")
            # imshow does not seem to support LogNorm for RGB data anymore
            if self.config["log"] and result.data.ndim != 3:
                self.image(
                    plt,
                    result.data,
                    result.extent,
                    norm=colors.LogNorm(vmin=vmin, vmax=vmax),
                    origin="lower",
                    cmap=self.config["colorscale"],
                    colorbar=colorbar,
                )
            else:
                self.image(plt, result.data, result.extent, vmin=vmin, vmax=vmax, origin="lower", cmap=self.config["colorscale"], colorbar=colorbar)

    def plot(self, plt: plt.axes, result: Result) -> plt.Figure:
        self.setupLabels()
        fig = plt.figure()
        super().showTimeIfDesired(fig, result)
        self.plotData(plt, result)
        return fig


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
