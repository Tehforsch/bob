import argparse

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors

from bob.simulation import Simulation
from bob.snapshot import Snapshot
from bob.postprocessingFunctions import SnapFn, addToList
from bob.result import Result
from bob.basicField import BasicField
from bob.temperature import Temperature


class TemperatureDensityHistogram(SnapFn):
    def post(self, args: argparse.Namespace, sim: Simulation, snap: Snapshot) -> Result:
        temperature = Temperature().getData(snap)
        density = BasicField("Density").getData(snap)
        print(np.min(temperature), np.mean(temperature), np.max(temperature))
        print(np.min(density), np.mean(density), np.max(density))
        return Result([temperature, density])

    def plot(self, plt: plt.axes, result: Result) -> None:
        fig = plt.figure()
        ax = fig.add_subplot(2, 1, 1)
        plt.xlabel("T [K]")
        plt.ylabel("$\\rho$")
        ax.set_xscale("log")
        ax.set_yscale("log")
        # minX = np.min(result.arrs[0])
        # maxX = np.max(result.arrs[0])
        # minY = np.min(result.arrs[1])
        # maxY = np.max(result.arrs[1])
        minX = 1e0
        maxX = 1e6
        minY = 1e-10
        maxY = 1e-4
        binsX = np.logspace(np.log10(minX), np.log10(maxX), num=104)
        binsY = np.logspace(np.log10(minY), np.log10(maxY), num=104)
        plt.xticks([1e0, 1e1, 1e2, 1e3, 1e4, 1e5, 1e6])
        plt.yticks([1e-10, 1e-8, 1e-6, 1e-4])
        plt.hist2d(result.arrs[0], result.arrs[1], [binsX, binsY], density=True, norm=colors.LogNorm())
        colorbar = plt.colorbar()
        colorbar.set_ticks([1e-5, 1e-0, 1e5])


addToList("temperatureDensityHistogram", TemperatureDensityHistogram())
