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
from bob.constants import protonMass


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
        config.setDefault("colors", ["r", "b", "g"])
        config.setDefault("labels", ["$32^3$", "$64^3$", "$128^3$"])
        super().__init__(config)

    def plotToBox(self, x: np.ndarray) -> np.ndarray:
        return x + self.center

    def getQuantity(self, sim: Simulation, snap: Snapshot) -> List[float]:
        lengthUnit = snap.lengthUnit
        self.L = sim.boxSize()
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
        densityThreshold = 100.0 * pq.cm ** (-3) * protonMass
        densities = densities.to(pq.g / pq.cm**3)
        print(sim, snap, len(np.where(densities < densityThreshold)[0]) / len(np.where(densities > densityThreshold)[0]))
        selection = np.array(
            [
                i
                for (i, coord) in enumerate(snap.coordinates)
                if (self.cone1.contains(coord) and self.cone2.contains(coord) and densities[i] < densityThreshold)
            ]
        )
        data = snap.ionized_hydrogen_fraction()[selection]
        masses = BasicField("Masses").getData(snap)[selection]
        return np.sum(data * masses) / np.sum(masses)

    def plot(self, plt: plt.axes, result: Result) -> None:
        super().plot(plt, result)
        plt.xlim(0, 60)
        plt.ylim(0, 1.0)
        plt.legend(loc="upper left")
