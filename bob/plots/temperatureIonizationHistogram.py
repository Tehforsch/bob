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
    def setArgs(self, subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument("--only_ionized", action="store_true")

    def getName(self, args: argparse.Namespace) -> str:
        ionizedStr = "_only_ionized" if args.only_ionized else ""
        return f"{self.name}_{ionizedStr}"

    def post(self, args: argparse.Namespace, sim: Simulation, snap: Snapshot) -> Result:
        temperature = Temperature().getData(snap) / pq.K
        ionization = BasicField("ChemicalAbundances", 1).getData(snap)
        print(np.min(temperature), np.mean(temperature), np.max(temperature))
        print(np.min(ionization), np.mean(ionization), np.max(ionization))
        return Result([temperature, ionization])

    def plot(self, plt: plt.axes, result: Result) -> None:
        fig = plt.figure()
        ax = fig.add_subplot(2, 1, 1)
        plt.xlabel("$x_{\mathrm{H}}$")
        plt.ylabel("T [K]")
        ax.set_xscale("log")
        ax.set_yscale("log")
        minX = 1e-6
        maxX = 1e0
        minY = 5e0
        maxY = 2e6
        binsX = np.logspace(np.log10(minX), np.log10(maxX), num=104)
        binsY = np.logspace(np.log10(minY), np.log10(maxY), num=104)
        plt.xticks([1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1e0])
        plt.yticks([1e0, 1e1, 1e2, 1e3, 1e4, 1e5, 1e6, 1e7])
        plt.hist2d(result.arrs[1], result.arrs[0], [binsX, binsY], density=True, norm=colors.LogNorm())
        colorbar = plt.colorbar()
        colorbar.set_ticks([1e-6, 1e-4, 1e-2, 1e0, 1e2])


addToList("temperatureIonizationHistogram", TemperatureIonizationHistogram())
