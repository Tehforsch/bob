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

    def ylabel(self) -> str:
        return "$x_{\\mathrm{H+}}$"

    def getQuantity(self, sim: Simulation, snap: Snapshot) -> List[float]:
        densityUnit = pq.g / pq.cm**3 * cu.littleh**2
        data = []
        self.densityBins = [x * densityUnit for x in [1e-31, 1e-29, 1e-27, 1e-25]]
        density = BasicField("Density").getData(snap).to(densityUnit, cu.with_H0(snap.H0))
        for (density1, density2) in zip(self.densityBins, self.densityBins[1:]):
            allIndices = np.where((density1 < density) & (density < density2))
            skip = int(allIndices[0].shape[0] / self.config["numSamples"])
            indices = allIndices[0][::skip]
            masses = BasicField("Masses").getData(snap, indices=indices)
            ionization = BasicField("ChemicalAbundances", 1).getData(snap, indices=indices)
            avIonization = np.sum(ionization * masses / np.sum(masses))
            print(density1, density2, np.mean(avIonization))
            data.append(avIonization)
        return getArrayQuantity(data)

    def plot(self, plt: plt.axes, result: Result) -> None:
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.set_yscale("log")
        sublabels = [
            "$\\rho = 10^{-31} - 10^{-29} \\mathrm{g} / \\mathrm{cm}^3$",
            "$\\rho = 10^{-29} - 10^{-27} \\mathrm{g} / \\mathrm{cm}^3$",
            "$\\rho = 10^{-27} - 10^{-25} \\mathrm{g} / \\mathrm{cm}^3$",
        ]
        colors = ["r", "g", "b"]
        for (color, label) in zip(colors, sublabels):
            plt.plot([], [], color=color, label=label)

        plt.xlabel(self.xlabel())
        plt.ylabel(self.ylabel())
        plt.xlim(self.config["xLim"])
        plt.ylim((1e-6, 1e0))
        for result in result.data:
            for (i, color) in zip(range(result.values.shape[1]), colors):
                plt.plot(result.times, result.values[:, i], color=color)
        plt.legend(loc="lower left")
