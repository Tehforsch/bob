import argparse

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import astropy.units as pq

from bob.simulation import Simulation
from bob.snapshot import Snapshot
from bob.postprocessingFunctions import SnapFn, addToList
from bob.result import Result
from bob.basicField import BasicField
from bob.temperature import Temperature


class TemperatureIonizationHistogram(SnapFn):
    def post(self, args: argparse.Namespace, sim: Simulation, snap: Snapshot) -> Result:
        result = Result()
        result.temperature = Temperature().getData(snap) / pq.K
        result.ionization = BasicField("ChemicalAbundances", 1).getData(snap)
        print(np.min(result.temperature), np.mean(result.temperature), np.max(result.temperature))
        print(np.min(result.ionization), np.mean(result.ionization), np.max(result.ionization))
        return result

    def plot(self, plt: plt.axes, result: Result) -> None:
        fig = plt.figure()
        ax = fig.add_subplot(2, 1, 1)
        self.style.setDefault("xUnit", pq.dimensionless_unscaled)
        self.style.setDefault("yUnit", pq.K)
        self.style.setDefault("xLabel", "$x_{\\mathrm{H}} [UNIT]$")
        self.style.setDefault("yLabel", "T [UNIT]")
        self.setupLabels()
        ax.set_xscale("log")
        ax.set_yscale("log")
        minX = 1e-10
        maxX = 1e0
        minY = 5e0
        maxY = 1e5
        binsX = np.logspace(np.log10(minX), np.log10(maxX), num=104)
        binsY = np.logspace(np.log10(minY), np.log10(maxY), num=104)
        plt.xticks([1e-10, 1e-8, 1e-6, 1e-4, 1e-2, 1e0])
        plt.yticks([1e0, 1e1, 1e2, 1e3, 1e4, 1e5])
        plt.hist2d(result.ionization, result.temperature, [binsX, binsY], density=True, norm=colors.LogNorm())
        colorbar = plt.colorbar()
        colorbar.set_ticks([1e-9, 1e-6, 1e-3, 1e0, 1e3])


addToList("temperatureIonizationHistogram", TemperatureIonizationHistogram())
