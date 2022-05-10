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

    def getQuantity(self, args: argparse.Namespace, sims: Simulation, snap: Snapshot) -> List[float]:
        density = BasicField("Density").getData(snap) / (pq.g / pq.cm**3)
        masses = BasicField("Masses").getData(snap)
        temperature = Temperature().getData(snap) / pq.K
        minDens = 1e-31
        maxDens = 1e-24
        self.densityBins = np.logspace(np.log10(minDens), np.log10(maxDens), num=8)
        result = []
        for (density1, density2) in zip(self.densityBins, self.densityBins[1:]):
            indices = np.where((density1 < density) & (density < density2))
            avTemp = np.sum(temperature[indices] * masses[indices] / np.sum(masses[indices]))
            print(f"{density1}-{density2}: {avTemp} K")
            result.append(np.sum(temperature[indices] * masses[indices] / np.sum(masses[indices])))
        return result

    def plot(self, plt: plt.axes, result: Result) -> None:
        self.labels = [[
            "$10^{-31} - 10^{-30}$",
            "$10^{-30} - 10^{-29}$",
            "$10^{-29} - 10^{-28}$",
            "$10^{-28} - 10^{-27}$",
            "$10^{-27} - 10^{-26}$",
            "$10^{-26} - 10^{-25}$",
            "$10^{-25} - 10^{-24}$"]]

        super().plot(plt, result)
        # fig = plt.figure()
        # ax = fig.add_subplot(1, 1, 1)
        # ax.set_yscale("log")


addToList("temperatureOverTime", TemperatureOverTime())
