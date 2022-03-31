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
from bob.field import Field
from bob.plots.bobSlice import getDataAtPoints
from bob.basicField import BasicField
from bob.simulation import Simulation


class ShadowingLinePlot(TimePlot):
    def xlabel(self) -> str:
        return "$t \; [\mathrm{Myr}]$"

    def ylabel(self) -> str:
        return "$\overline{x_{\mathrm{H}}}$"

    def getQuantity(self, args: argparse.Namespace, sims: Simulation, snap: Snapshot) -> float:
        startRadius = (4 / 16) / np.sqrt(2)
        safetyFactor = 1.1
        start = np.array([0.5 + startRadius * safetyFactor, 0.5 + startRadius * safetyFactor, 0.5])
        end = np.array([1.0, 1.0, 0.5])
        data = self.getDataAlongLine(BasicField("ChemicalAbundances", 1), snap, start, end)
        masses = self.getDataAlongLine(BasicField("Masses"), snap, start, end)
        return np.sum(data * masses) / np.sum(masses)

    def transform(self, result: np.ndarray) -> np.ndarray:
        result[0, :] = result[0, :] * ((config.defaultTimeUnit / pq.kyr).decompose().to(1))
        return result

    def getDataAlongLine(self, field: Field, snap: Snapshot, start: np.ndarray, end: np.ndarray) -> np.ndarray:
        numPoints = 2000
        fractions = np.linspace(0.0, 1.0, numPoints)
        offsets = np.outer(end - start, fractions).transpose()
        points = np.add(start, offsets)
        return getDataAtPoints(field, snap, points)

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


addToList("shadowingLine", ShadowingLinePlot())
