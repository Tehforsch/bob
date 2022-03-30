import argparse
from typing import List
import astropy.units as pq
from bob.simulationSet import SimulationSet
import matplotlib.pyplot as plt
import numpy as np

from bob.simulation import Simulation
from bob.snapshot import Snapshot
from bob.postprocessingFunctions import addToList
from bob.basicField import BasicField
from bob.constants import speedOfLight, protonMass
from bob.plots.timePlots import TimePlot
from bob.result import Result


class ThomsonScattering(TimePlot):
    def getQuantity(self, args: argparse.Namespace, sim: Simulation, snap: Snapshot) -> None:
        sig = 6.65e-29 * pq.m**2  # Thomson scattering cross-section
        xe = BasicField("Density").getData(snap)
        print("DEFINITELY TODO")
        density = BasicField("Density").getData(snap) * snap.lengthUnit ** (-3) * snap.massUnit
        ne = xe * density / protonMass
        self.timeUnit = pq.yr
        return speedOfLight * sig * np.mean(ne) * self.timeUnit

    def plot(self, plt: plt.axes, result: Result) -> None:
        super().plot(plt, result)
        nx = int(50)
        ztau = np.linspace(0.0, 50.0, nx)
        taumax = np.full(nx, 0.061)
        taumin = np.full(nx, 0.047)

        plt.fill_between(ztau, taumin, taumax, facecolor="gray", alpha=0.25, label=r"Planck+18")

    def transform(self, result: np.ndarray) -> np.ndarray:
        dt = np.diff(result[0, :], 1) * self.timeUnit
        newResult = np.zeros((2, result.shape[1] - 1))
        newResult[0, :] = result[0, 1:]
        newResult[1, :] = np.cumsum(result[1, 1:] * dt)
        return newResult

    def ylabel(self):
        return "$\tau$"


addToList("thomsonScattering", ThomsonScattering())
