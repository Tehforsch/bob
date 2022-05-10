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
        densities = BasicField("Density").getData(snap)
        masses = BasicField("Masses").getData(snap)
        temperature = Temperature().getData(snap) / pq.K
        minDens = 1e-33
        maxDens = 1e-24
        densities = np.logspace(np.log10(minDens), np.log10(maxDens), num=10)
        result = []
        for (density1, density2) in zip(densities, densities[1:]):
            indices = np.where((density1 < densities) & (densities < density2))
            result.append(np.sum(temperature[indices] * masses[indices] / np.sum(masses[indices])))
        return result

    def plot(self, plt: plt.axes, result: Result) -> None:
        super().plot(plt, result)
        plt.legend(loc="upper left")


addToList("temperatureOverTime", TemperatureOverTime())
