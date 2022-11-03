from typing import List

import numpy as np
import matplotlib.pyplot as plt
import astropy.units as pq
import astropy.cosmology.units as cu

from bob.result import Result
from bob.plots.timePlots import TimePlot
from bob.snapshot import Snapshot
from bob.basicField import BasicField
from bob.simulation import Simulation
from bob.plotConfig import PlotConfig
from bob.util import getArrayQuantity


class IonizationBinned(TimePlot):
    def __init__(self, config: PlotConfig) -> None:
        super().__init__(config)
        self.config.setDefault("numSamples", 100000)
        self.config.setDefault("xLim", [10.0, 4.2])
        self.config.setDefault("densityFactors", [1.0 / 10.0, 1.0 / 2.0, 1.0, 2.0, 10.0])
        self.config.setDefault(
            "sublabels",
            [
                "$1/10 \\langle \\rho \\rangle$",
                "$1/2 \\langle \\rho \\rangle$",
                "$1 \\langle \\rho \\rangle$",
                "$2 \\langle \\rho \\rangle$",
                "$10 \\langle \\rho \\rangle$",
            ],
        )
        self.config.setDefault("colors", ["r", "g", "b", "brown", "orange"])

    def ylabel(self) -> str:
        return "$x_{\\mathrm{H+}}$"

    def getQuantity(self, sim: Simulation, snap: Snapshot) -> List[float]:
        densityUnit = pq.g / pq.cm**3 * cu.littleh**2
        data = []
        density = BasicField("Density").getData(snap).to(densityUnit, cu.with_H0(snap.H0))
        meanDensity = np.mean(density)
        densities = [meanDensity * factor for factor in self.config["densityFactors"]]
        epsilon = 0.01
        densityBins = [[dens * (1 - epsilon), dens * (1 + epsilon)] for dens in densities]
        for (density1, density2) in densityBins:
            allIndices = np.where((density1 < density) & (density < density2))
            skip = max(1, int(allIndices[0].shape[0] / self.config["numSamples"]))
            indices = allIndices[0][::skip]
            masses = BasicField("Masses").getData(snap, indices=indices)
            ionization = BasicField("ChemicalAbundances", 1).getData(snap, indices=indices)
            avIonization = np.sum(ionization * masses / np.sum(masses))
            print(f"{density1} - {density2}: {np.mean(avIonization)} ({indices.shape} values)")
            data.append(avIonization)
        return getArrayQuantity(data)

    def plot(self, plt: plt.axes, result: Result) -> None:
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.set_yscale("log")
        for (color, label) in zip(self.config["colors"], self.config["sublabels"]):
            plt.plot([], [], color=color, label=label)

        plt.xlabel(self.xlabel())
        plt.ylabel(self.ylabel())
        plt.xlim(self.config["xLim"])
        plt.ylim((1e-6, 1e0))
        for result in result.data:
            for (i, color) in zip(range(result.values.shape[1]), self.config["colors"]):
                plt.plot(result.times, result.values[:, i], color=color)
        plt.legend(loc="lower left")
