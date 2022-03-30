import argparse

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
        return "Mass av."

    def getQuantity(self, args: argparse.Namespace, sims: Simulation, snap: Snapshot) -> float:
        start = np.array([0.5, 0.5, 0.5])
        end = np.array([1.0, 1.0, 0.5])
        data = self.getDataAlongLine(BasicField("ChemicalAbundances", 1), snap, start, end)
        print(snap.time, np.mean(data))
        masses = self.getDataAlongLine(BasicField("Masses"), snap, start, end)
        return np.sum(data * masses) / np.sum(masses)

    def transform(self, result: np.ndarray) -> np.ndarray:
        result[0, :] = result[0, :] * ((config.defaultTimeUnit / pq.kyr).decompose().to(1))
        return result

    def getDataAlongLine(self, field: Field, snap: Snapshot, start: np.ndarray, end: np.ndarray) -> np.ndarray:
        numPoints = 2000
        result = np.zeros((2, numPoints))
        fractions = np.linspace(0.0, 1.0, numPoints)
        offsets = np.outer(end - start, fractions).transpose()
        points = np.add(start, offsets)
        result[1, :] = getDataAtPoints(field, snap, points)
        result[0, :] = fractions
        return result

    def plot(self, plt: plt.axes, result: Result) -> None:
        super().plot(plt, result)
        plt.ylim(0, 1)


addToList("shadowingLine", ShadowingLinePlot())
