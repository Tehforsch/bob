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


class TemperatureDensityHistogram(SnapFn):
    def setArgs(self, subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument("--only_ionized", action="store_true")

    def getName(self, args: argparse.Namespace) -> str:
        ionizedStr = "_only_ionized" if args.only_ionized else ""
        return f"{self.name}{ionizedStr}"

    def post(self, args: argparse.Namespace, sim: Simulation, snap: Snapshot) -> Result:
        result = Result()
        result.temperature = Temperature().getData(snap) / pq.K
        result.density = BasicField("Density").getData(snap) / (pq.g / pq.cm**3)
        if args.only_ionized:
            hpAbundance = BasicField("ChemicalAbundances", 1).getData(snap)
            indices = np.where(hpAbundance > 0.5)
            result.temperature = result.temperature[indices]
            result.density = result.density[indices]
        print(np.min(result.temperature), np.mean(result.temperature), np.max(result.temperature))
        print(np.min(result.density), np.mean(result.density), np.max(result.density))
        return result

    def plot(self, plt: plt.axes, result: Result) -> None:
        fig = plt.figure()
        ax = fig.add_subplot(2, 1, 1)
        self.style.setDefault("xUnit", "g / cm^3")
        self.style.setDefault("yUnit", "K")
        self.style.setDefault("xLabel", "$\\rho [UNIT]$")
        self.style.setDefault("yLabel", "T [UNIT]")
        self.setupLabels()
        ax.set_xscale("log")
        ax.set_yscale("log")
        minX = 1e-31
        maxX = 5e-26
        minY = 5e0
        maxY = 2e6
        binsX = np.logspace(np.log10(minX), np.log10(maxX), num=104)
        binsY = np.logspace(np.log10(minY), np.log10(maxY), num=104)
        plt.xticks([1e-31, 1e-30, 1e-29, 1e-28, 1e-27, 1e-26])
        plt.yticks([1e0, 1e1, 1e2, 1e3, 1e4, 1e5, 1e6, 1e7])
        plt.hist2d(result.density, result.temperature, [binsX, binsY], density=True, norm=colors.LogNorm())
        colorbar = plt.colorbar()
        colorbar.set_ticks([1e17, 1e22, 1e27])


addToList("temperatureDensityHistogram", TemperatureDensityHistogram())
