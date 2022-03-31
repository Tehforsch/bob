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
    def __init__(self, tip: np.ndarray, normal: np.ndarray, radiusPerDistance: float) -> None:
        self.tip = tip
        self.normal = normal
        self.radiusPerDistance = radiusPerDistance

    def contains(self, point: np.ndarray) -> bool:
        dist = point - self.tip
        lengthAlongCentralLine = np.dot(dist, self.normal)
        if lengthAlongCentralLine < 0:
            return False
        coneRadiusAtPoint = lengthAlongCentralLine * self.radiusPerDistance
        orthogonalDistance = np.linalg.norm((point - self.tip) - lengthAlongCentralLine * self.normal)
        return coneRadiusAtPoint >= orthogonalDistance


class ShadowingVolumePlot(TimePlot):
    def __init__(self) -> None:
        super().__init__()
        self.L = 32
        self.boxSize = 1.0

    def plotToBox(self, x: np.ndarray) -> np.ndarray:
        center = np.array([self.boxSize / 2.0, self.boxSize / 2.0, self.boxSize / 2.0])
        return (x - center) * self.L

    def init(self, args: argparse.Namespace) -> None:
        distanceFromCenter = 14.0
        radiusBlob = 4.0
        self.cone1 = InfiniteCone(
            self.plotToBox(np.array([-distanceFromCenter, 0.0, 0.0])), np.array([1.0, 0.0, 0.0]), radiusBlob / distanceFromCenter
        )
        self.cone2 = InfiniteCone(
            self.plotToBox(np.array([0.0, -distanceFromCenter, 0.0])), np.array([0.0, 1.0, 0.0]), radiusBlob / distanceFromCenter
        )

    def xlabel(self) -> str:
        return "$t \; [\mathrm{Myr}]$"

    def ylabel(self) -> str:
        return "$\overline{x_{\mathrm{H}}}$"

    def getQuantity(self, args: argparse.Namespace, sims: Simulation, snap: Snapshot) -> float:
        selection = np.array([(1 if self.cone1.contains(coord) & self.cone2.contains(coord) else 0) for coord in snap.coordinates])
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
