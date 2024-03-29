from typing import List

import numpy as np
import matplotlib.pyplot as plt
import astropy.units as pq

from bob.result import Result
from bob.snapshot import Snapshot
from bob.basicField import BasicField
from bob.simulation import Simulation
from bob.temperature import Temperature
from bob.plotConfig import PlotConfig
from bob.plots.meanFieldOverTime import MeanFieldOverTime


class TemperatureOverTime(MeanFieldOverTime):
    def __init__(self, config: PlotConfig) -> None:
        super().__init__(config)
        time = self.config["time"]
        self.config.setDefault("name", f"{self.name}_{time}_binned")
        self.config.setDefault("yLim", [1e3, 1e5])

    def ylabel(self) -> str:
        return "$T [\\mathrm{K}]$"

    def getQuantity(self, sim: Simulation, snap: Snapshot) -> List[float]:  # type: ignore
        density = BasicField("Density").getData(snap) / (pq.g / pq.cm**3)
        masses = BasicField("Masses").getData(snap)
        temperature = Temperature().getData(snap) / pq.K
        result = []
        self.densityBins = [1e-31, 1e-29, 1e-27, 1e-25]
        for density1, density2 in zip(self.densityBins, self.densityBins[1:]):
            indices = np.where((density1 < density) & (density < density2))
            avTemp = np.sum(temperature[indices] * masses[indices] / np.sum(masses[indices]))
            result.append(avTemp)
            result.append(avTemp)
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
        subcolors = [
            "b",
            "r",
            "g",
        ]

        plt.xlabel(self.xlabel())
        plt.ylabel(self.ylabel())
        plt.xlim(self.config["xLim"])
        plt.ylim(self.config["yLim"])
        for i, (res, label) in enumerate(zip(result.data, self.config["labels"])):
            for i, (sublabel, subcolor) in enumerate(zip(sublabels, subcolors)):
                plt.plot(res.times, res.values[:, i], color=subcolor)

        for sublabel, subcolor in zip(sublabels, subcolors):
            plt.plot([], [], color=subcolor, label=sublabel)
        plt.legend(loc="lower left")
        if self.config["time"] == "t":
            self.addConstraints(plt)

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
