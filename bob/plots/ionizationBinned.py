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

    def ylabel(self) -> str:
        return "$x_{\\mathrm{H+}}$"

    def getQuantity(self, sim: Simulation, snap: Snapshot) -> List[float]:
        densityUnit = pq.g / pq.cm**3 * cu.littleh**2
        density = BasicField("Density").getData(snap)
        masses = BasicField("Masses").getData(snap)
        ionization = BasicField("ChemicalAbundances", 1).getData(snap)
        data = []
        self.densityBins = [x * densityUnit for x in [1e-31, 1e-29, 1e-27, 1e-25]]
        for (density1, density2) in zip(self.densityBins, self.densityBins[1:]):
            indices = np.where((density1 < density) & (density < density2))
            avTemp = np.sum(ionization[indices] * masses[indices] / np.sum(masses[indices]))
            data.append(avTemp)
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

        plt.xlabel(self.xlabel())
        plt.ylabel(self.ylabel())
        plt.xlim((55, 6))
        plt.ylim((1e-6, 1e0))
        for result in result.data:
            for (i, label) in zip(range(result.values.shape[1]), sublabels):
                plt.plot(result.times, result.values[:, i], label=label)
        plt.legend(loc="lower left")
