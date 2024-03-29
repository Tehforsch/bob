from typing import List

import numpy as np
import matplotlib.pyplot as plt
import astropy.units as pq

from bob.result import Result
from bob.plots.timePlots import TimePlot
from bob.snapshot import Snapshot
from bob.basicField import BasicField
from bob.simulation import Simulation
from bob.plotConfig import PlotConfig


class InfiniteCone:
    def __init__(self, tip: np.ndarray, normal: np.ndarray, radiusPerDistance: float, start: np.ndarray) -> None:
        self.tip = tip
        self.normal = normal
        self.radiusPerDistance = radiusPerDistance
        self.start = np.dot(start, self.normal)

    def contains(self, point: np.ndarray) -> bool:
        dist = point - self.tip
        lengthAlongCentralLine = np.dot(dist, self.normal)
        if lengthAlongCentralLine < self.start:
            return False
        coneRadiusAtPoint = lengthAlongCentralLine * self.radiusPerDistance
        orthogonalDistance = np.linalg.norm((point - self.tip) - lengthAlongCentralLine * self.normal)
        return coneRadiusAtPoint >= orthogonalDistance


class ShadowingVolume(TimePlot):
    def __init__(self, config: PlotConfig) -> None:
        config.setDefault("xUnit", pq.kyr)
        config.setDefault("yUnit", 1.0)
        config.setDefault("xLabel", "$t \; [\mathrm{kyr}]$")
        config.setDefault("yLabel", "$\overline{x_{\mathrm{H}}}$")
        config.setDefault("colors", ["b", "b", "b", "r", "r", "r"])
        super().__init__(config)

    def plotToBox(self, x: np.ndarray) -> np.ndarray:
        return x + self.center

    def getQuantity(self, sim: Simulation, snap: Snapshot) -> List[float]:
        lengthUnit = snap.lengthUnit
        self.L = 1.0 * lengthUnit
        self.center = self.L * np.array([0.5, 0.5, 0.5])
        self.plotCenter = np.array([0.5, 0.5, 0.5])
        distanceFromCenter = 14.0 / 32.0 * self.L
        radiusBlob = 4.0 / 32.0 * self.L
        self.cone1 = InfiniteCone(
            self.plotToBox(distanceFromCenter * np.array([-1.0, 0.0, 0.0])), np.array([1.0, 0.0, 0.0]), radiusBlob / distanceFromCenter, self.center
        )
        self.cone2 = InfiniteCone(
            self.plotToBox(distanceFromCenter * np.array([0.0, -1.0, 0.0])), np.array([0.0, 1.0, 0.0]), radiusBlob / distanceFromCenter, self.center
        )
        densities = BasicField("Density").getData(snap)
        densityThreshold = 1500 * snap.massUnit / (snap.lengthUnit**3)
        selection = np.array(
            [
                i
                for (i, coord) in enumerate(snap.coordinates)
                if (self.cone1.contains(coord) and self.cone2.contains(coord) and densities[i] < densityThreshold)
            ]
        )
        data = BasicField("ChemicalAbundances", 1).getData(snap)[selection]
        masses = BasicField("Masses").getData(snap)[selection]
        return np.sum(data * masses) / np.sum(masses)

    def plot(self, plt: plt.axes, result: Result) -> None:
        super().plot(plt, result)
        plt.xlim(0, 60)
        plt.ylim(0, 1.0)
        plt.plot([], [], label="Sweep", color="b")
        plt.plot([], [], label="SPRAI", color="r")
        plt.plot([], [], label="$128^3$", linestyle="-", color="black")
        plt.plot([], [], label="$64^3$", linestyle="--", color="black")
        plt.plot([], [], label="$32^3$", linestyle=":", color="black")
        plt.legend(loc="upper left")
