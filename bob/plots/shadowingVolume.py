import argparse
import itertools

import numpy as np
import matplotlib.pyplot as plt
import astropy.units as pq

import bob.config as config
from bob.result import Result
from bob.postprocessingFunctions import addToList
from bob.plots.timePlots import TimePlot
from bob.snapshot import Snapshot
from bob.basicField import BasicField
from bob.simulation import Simulation


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


class ShadowingVolumePlot(TimePlot):
    def __init__(self) -> None:
        super().__init__()
        self.L = 32
        self.boxSize = 1.0
        self.center = np.array([self.boxSize / 2.0, self.boxSize / 2.0, self.boxSize / 2.0])

    def plotToBox(self, x: np.ndarray) -> np.ndarray:
        return x / self.L + self.center

    def init(self, args: argparse.Namespace) -> None:
        distanceFromCenter = 14.0
        radiusBlob = 4.0
        self.cone1 = InfiniteCone(
            self.plotToBox(np.array([-distanceFromCenter, 0.0, 0.0])), np.array([1.0, 0.0, 0.0]), radiusBlob / distanceFromCenter, self.center
        )
        self.cone2 = InfiniteCone(
            self.plotToBox(np.array([0.0, -distanceFromCenter, 0.0])), np.array([0.0, 1.0, 0.0]), radiusBlob / distanceFromCenter, self.center
        )

    def xlabel(self) -> str:
        return "$t \; [\mathrm{kyr}]$"

    def ylabel(self) -> str:
        return "$\overline{x_{\mathrm{H}}}$"

    def getQuantity(self, args: argparse.Namespace, sims: Simulation, snap: Snapshot) -> float:
        print("At", sims.name, snap.time.to(pq.kyr))
        densities = BasicField("Density").getData(snap)
        densityThreshold = 1500
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

    def transform(self, result: np.ndarray) -> np.ndarray:
        result[0, :] = result[0, :] * ((config.defaultTimeUnit / pq.kyr).decompose().to(1))
        return result

    def plot(self, plt: plt.axes, result: Result) -> None:
        self.styles = [{"color": s[0], "linestyle": s[1]} for s in itertools.product(["r", "b"], ["-", "--", ":"])]
        self.labels = ["" for _ in result.arrs]

        super().plot(plt, result)
        plt.ylim(0, 0.45)
        plt.xlim(35, 60)
        plt.plot([], [], label="Sweep", color="b")
        plt.plot([], [], label="SPRAI", color="r")
        plt.plot([], [], label="$128^3$", linestyle="-", color="black")
        plt.plot([], [], label="$64^3$", linestyle="--", color="black")
        plt.plot([], [], label="$32^3$", linestyle=":", color="black")
        plt.legend()


addToList("shadowingVolume", ShadowingVolumePlot())
