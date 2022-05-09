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
        return f"{self.name}_{ionizedStr}"

    def post(self, args: argparse.Namespace, sim: Simulation, snap: Snapshot) -> Result:
        temperature = Temperature().getData(snap) / pq.K
        density = BasicField("Density").getData(snap) / (pq.g / pq.cm**3)
        print(np.min(temperature), np.mean(temperature), np.max(temperature))
        print(np.min(density), np.mean(density), np.max(density))
        return Result([temperature, density])

    def plot(self, plt: plt.axes, result: Result) -> None:
        fig = plt.figure()
        ax = fig.add_subplot(2, 1, 1)
        plt.xlabel("$\\rho [\mathrm{g} / \mathrm{cm}^3]$")
        plt.ylabel("T [K]")
        ax.set_xscale("log")
        ax.set_yscale("log")
        # minX = np.min(result.arrs[0])
        # maxX = np.max(result.arrs[0])
        # minY = np.min(result.arrs[1])
        # maxY = np.max(result.arrs[1])
        minX = 1e-31
        maxX = 5e-26
        minY = 5e0
        maxY = 2e6
        binsX = np.logspace(np.log10(minX), np.log10(maxX), num=104)
        binsY = np.logspace(np.log10(minY), np.log10(maxY), num=104)
        plt.xticks([1e-31, 1e-30, 1e-29, 1e-28, 1e-27, 1e-26])
        plt.yticks([1e0, 1e1, 1e2, 1e3, 1e4, 1e5, 1e6, 1e7])
        print(result.arrs[0])
        print(result.arrs[1])
        plt.hist2d(result.arrs[1], result.arrs[0], [binsX, binsY], density=True, norm=colors.LogNorm())
        colorbar = plt.colorbar()
        colorbar.set_ticks([1e17, 1e22, 1e27])


addToList("temperatureDensityHistogram", TemperatureDensityHistogram())
