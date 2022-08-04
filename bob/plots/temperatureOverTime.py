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

    def getName(self, args: argparse.Namespace) -> str:
        binString = "_binned" if self.config["bins"] else ""
        return f"{self.name}_{args.time}{binString}"

    def getQuantity(self, sim: Simulation, snap: Snapshot) -> List[float]:
        density = BasicField("Density").getData(snap) / (pq.g / pq.cm**3)
        masses = BasicField("Masses").getData(snap)
        temperature = Temperature().getData(snap) / pq.K
        result = []
        if self.config["bins"]:
            self.densityBins = [1e-31, 1e-29, 1e-27, 1e-25]
            for (density1, density2) in zip(self.densityBins, self.densityBins[1:]):
                indices = np.where((density1 < density) & (density < density2))
                avTemp = np.sum(temperature[indices] * masses[indices] / np.sum(masses[indices]))
                result.append(avTemp)
        else:
            avTemp = np.sum(temperature * masses / np.sum(masses))
            result.append(avTemp)
        return result

    def plot(self, plt: plt.axes, result: Result) -> None:
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.set_yscale("log")
        if self.config["bins"]:
            sublabels = [
                "$\\rho = 10^{-31} - 10^{-29} \mathrm{g} / \mathrm{cm}^3$",
                "$\\rho = 10^{-29} - 10^{-27} \mathrm{g} / \mathrm{cm}^3$",
                "$\\rho = 10^{-27} - 10^{-25} \mathrm{g} / \mathrm{cm}^3$",
            ]
        else:
            sublabels = [""]

        plt.xlabel(self.xlabel())
        plt.ylabel(self.ylabel())
        plt.ylim((1e1, 1e5))
        for (labels, arr) in zip(self.getLabels(), result.arrs):
            for (i, label) in zip(range(1, arr.shape[1]), sublabels):
                plt.plot(arr[:, 0], arr[:, i], label=label)
        plt.legend(loc="lower left")
        if self.config["time"] == "t":
            self.addConstraints(plt)

    def setArgs(self) -> None:
        super().setArgs()
        self.config.setDefault("bins", False)

    def addConstraints(self, ax: plt.axes) -> None:
        if self.config["time"] == "z":
            boera19_temps = np.asarray([[4.6, 7.31e3, 0.88e3, 1.35e3], [5.0, 7.37e3, 1.39e3, 1.67e3]])

            walther19_zeds = np.asarray([4.6, 5.0, 5.4])
            walther19_temps = np.asarray([[0.877e4, 0.106e4, 0.130e4], [0.533e4, 0.091e4, 0.122e4], [0.599e4, 0.134e4, 0.152e4]])
            ax.errorbar(
                boera19_temps[:, 0],
                boera19_temps[:, 1],
                yerr=boera19_temps[:, 2:],
                label="Boera+19",
                c="k",
                ls="none",
                marker="D",
                capsize=3,
                elinewidth=1,
            )

            ax.errorbar(
                walther19_zeds - 0.01,
                walther19_temps[:, 0],
                yerr=walther19_temps[:, 1:].T,
                label="Walther+19",
                c="k",
                ls="none",
                marker="o",
                capsize=3,
                elinewidth=1,
            )


addToList("temperatureOverTime", TemperatureOverTime())
