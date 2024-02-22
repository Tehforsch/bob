import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import logging
import astropy.units as pq

from bob.simulation import Simulation
from bob.snapshot import Snapshot
from bob.result import Result
from bob.plots.bobSlice import getSlice
from bob.plotConfig import PlotConfig
from bob.basicField import DatasetUnavailableError, BasicField
from bob.postprocessingFunctions import MultiSetFn
from bob.multiSet import MultiSet
from bob.field import Field
from bob.constants import protonMass
from bob.volume import Volume
from math import *


class PhotonDensity(Field):
    def getData(snapshot):
        return BasicField("photon_rate").getData(snapshot) / Volume().getData(snapshot)


class Shadowing(MultiSetFn):
    def __init__(self, config: PlotConfig) -> None:
        super().__init__(config)
        config.setDefault("quotient", "single")
        config.setDefault("xUnit", "pc")
        config.setDefault("yUnit", "pc")
        config.setDefault("vUnit", "s^-1 cm^-3")
        config.setDefault("cLabel", "$R [\\text{s}^{-1} \\text{cm}^{-3}]$")

    def post(self, sims: MultiSet) -> Result:
        assert len(sims) == 3
        configs = [(sim, snap) for sim in sims for snap in get_snaps_at_times(sim[0])]
        result = Result()
        data = []
        for sim, snap in configs:
            print(sim, snap.time.to(pq.kyr))
            sl = getSlice(PhotonDensity, snap, "z", 0.55)
            data.append(sl[1].to(pq.s**-1 * pq.cm**-3))
            result.extent = list(sl[0])
        result.data = data
        return result

    def plot(self, plt: plt.axes, result: Result) -> None:
        fig, axes = plt.subplots(3, 3, figsize=(10, 8), sharex=True, sharey=True)
        plt.tight_layout(pad=0.00)
        vmin = 1e-15
        vmax = 1e-8
        shift = 16
        for ax, d in zip(axes.flat, result.data):
            print(np.min(d), np.max(d))
            xUnit = pq.Unit(self.config["xUnit"])
            yUnit = pq.Unit(self.config["yUnit"])
            extent = (
                result.extent[0].to_value(xUnit) - shift,
                result.extent[1].to_value(xUnit) - shift,
                result.extent[2].to_value(yUnit) - shift,
                result.extent[3].to_value(yUnit) - shift,
            )
            vUnit = pq.Unit(self.config["vUnit"])
            image = ax.imshow(d.to_value(vUnit), extent=extent, norm=colors.LogNorm(vmin=vmin, vmax=vmax), origin="lower", cmap="BuGn")
            ax.set_xlim([-14.2, 10])
            ax.set_ylim([-14.2, 10])
        xlabel = "x [\\text{pc}]"
        ylabel = "y [\\text{pc}]"
        axes[2][0].set_xlabel(xlabel)
        axes[2][1].set_xlabel(xlabel)
        axes[2][2].set_xlabel(xlabel)
        axes[0][0].set_ylabel(ylabel)
        axes[1][0].set_ylabel(ylabel)
        axes[2][0].set_ylabel(ylabel)

        cbar = fig.colorbar(image, ax=axes.ravel().tolist())
        cbar.set_label(self.config["cLabel"])

        for i, axes in enumerate(axes):
            for j, ax in enumerate(axes):
                ax.add_patch(plt.Circle((-14, 0), 0.4, color="white"))
                ax.add_patch(plt.Circle((0, -14), 0.4, color="white"))
                ax.add_patch(plt.Circle((0, 0), 4, facecolor="none", edgecolor="black", linestyle="--"))
                maxExtent = 10
                L = 16.0
                r = 4.0
                d = 14.0
                alpha = acos(sqrt(1 - r**2 / d**2))
                x1 = d + maxExtent
                y1 = x1 * tan(alpha)
                ax.plot([-d, maxExtent], [0, y1], color="black")
                ax.plot([0, y1], [-d, maxExtent], color="black")
                if (i, j) == (0, 0):
                    ax.annotate("3 \\text{kyr}", xy=(-4, 8), fontsize=15, color="red")
                if (i, j) == (0, 1):
                    ax.annotate("32 \\text{kyr}", xy=(-4, 8), fontsize=15, color="red")
                if (i, j) == (0, 2):
                    ax.annotate("48 \\text{kyr}", xy=(-4, 8), fontsize=15, color="red")

                if (i, j) == (0, 0):
                    ax.annotate("$32^3$", xy=(-12, -3), fontsize=15, color="blue")
                if (i, j) == (1, 0):
                    ax.annotate("$64^3$", xy=(-12, -3), fontsize=15, color="blue")
                if (i, j) == (2, 0):
                    ax.annotate("$128^3$", xy=(-12, -3), fontsize=15, color="blue")

        return fig


def get_snaps_at_times(sim):
    times = [3.0 * pq.kyr, 32 * pq.kyr, 48 * pq.kyr]
    return [findSnapAtTime(sim, time) for time in times]


def findSnapAtTime(sim, time):
    return min(sim.snapshots, key=lambda snap: abs(snap.time - time))
