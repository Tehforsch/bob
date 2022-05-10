from typing import List
import argparse
import itertools

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
        self.styles = [{"color": s[0], "linestyle": s[1]} for s in itertools.product(["r", "b"], ["-", "--", ":"])]
        self.labels = ["" for _ in result.arrs]

        print(result.arrs)
        super().plot(plt, result)
        # plt.xlim(0, 60)
        # plt.ylim(0, 1.0)
        # plt.plot([], [], label="Sweep", color="b")
        # plt.plot([], [], label="SPRAI", color="r")
        # plt.plot([], [], label="$128^3$", linestyle="-", color="black")
        # plt.plot([], [], label="$64^3$", linestyle="--", color="black")
        # plt.plot([], [], label="$32^3$", linestyle=":", color="black")
        plt.legend(loc="upper left")


addToList("temperatureOverTime", TemperatureOverTime())
