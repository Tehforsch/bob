from typing import List
import argparse

import numpy as np
import matplotlib.pyplot as plt
import astropy.units as pq

from bob.result import Result
from bob.postprocessingFunctions import addToList
from bob.plots.timePlots import TimePlot
from bob.snapshot import Snapshot
from bob.basicField import BasicField
from bob.simulation import Simulation
from bob.temperature import Temperature


class TemperatureOverTime(TimePlot):
    def ylabel(self) -> str:
        return "$T [\\mathrm{K}]$"

    def getQuantity(self, args: argparse.Namespace, sim: Simulation, snap: Snapshot) -> List[float]:
        redshiftStartOfSim = sim.getRedshift(sim.snapshots[0].scale_factor)
        redshiftNow = sim.getRedshift(snap.scale_factor)
        correctionFactor = (1 + redshiftNow) ** 2 / (1 + redshiftStartOfSim) ** 2
        density = BasicField("Density").getData(snap) / (pq.g / pq.cm**3)
        masses = BasicField("Masses").getData(snap)
        temperature = Temperature().getData(snap) / pq.K
        self.densityBins = [1e-31, 1e-29, 1e-27, 1e-25]
        result = []
        for (density1, density2) in zip(self.densityBins, self.densityBins[1:]):
            indices = np.where((density1 < density) & (density < density2))
            avTemp = np.sum(temperature[indices] * masses[indices] / np.sum(masses[indices]))
            print(f"{density1}-{density2}: {avTemp} K")
            result.append(correctionFactor * np.sum(temperature[indices] * masses[indices] / np.sum(masses[indices])))
        return result

    def plot(self, plt: plt.axes, result: Result) -> None:
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.set_yscale("log")
        sublabels = [
            "$\\rho = 10^{-31} - 10^{-29} \mathrm{g} / \mathrm{cm}^3$",
            "$\\rho = 10^{-29} - 10^{-27} \mathrm{g} / \mathrm{cm}^3$",
            "$\\rho = 10^{-27} - 10^{-25} \mathrm{g} / \mathrm{cm}^3$",
        ]

        plt.xlabel(self.xlabel())
        plt.ylabel(self.ylabel())
        plt.ylim((1e1, 1e5))
        for (style, labels, arr) in zip(self.styles, self.labels, result.arrs):
            for (i, label) in zip(range(1, arr.shape[1]), sublabels):
                plt.plot(arr[:, 0], arr[:, i], label=label)
        plt.legend(loc="lower left")


addToList("temperatureOverTime", TemperatureOverTime())
