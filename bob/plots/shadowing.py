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
        config.setDefault("cLabel", "$R [\\text{s}^-1 \\text{cm}^-3]$")

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
        for ax, d in zip(axes.flat, result.data):
            print(np.min(d), np.max(d))
            xUnit = pq.Unit(self.config["xUnit"])
            yUnit = pq.Unit(self.config["yUnit"])
            extent = (
                result.extent[0].to_value(xUnit),
                result.extent[1].to_value(xUnit),
                result.extent[2].to_value(yUnit),
                result.extent[3].to_value(yUnit),
            )
            vUnit = pq.Unit(self.config["vUnit"])
            image = ax.imshow(d.to_value(vUnit), extent=extent, norm=colors.LogNorm(vmin=vmin, vmax=vmax), origin="lower", cmap="Reds")
        xlabel = "x [\\text{pc}]"
        ylabel = "y [\\text{pc}]"
        axes[2][0].set_xlabel(xlabel)
        axes[2][1].set_xlabel(xlabel)
        axes[2][2].set_xlabel(xlabel)
        axes[0][0].set_ylabel(ylabel)
        axes[1][0].set_ylabel(ylabel)
        axes[2][0].set_ylabel(ylabel)

        axes[0][0].annotate("3.0 \\text{kyr}", xy=(22, 29), fontsize=15)
        axes[0][1].annotate("32.0 \\text{kyr}", xy=(22, 29), fontsize=15)
        axes[0][2].annotate("48.0 \\text{kyr}", xy=(22, 29), fontsize=15)

        axes[0][0].annotate("$32^3$", xy=(1.5, 29), fontsize=15)
        axes[1][0].annotate("$64^3$", xy=(1.5, 29), fontsize=15)
        axes[2][0].annotate("$128^3$", xy=(1.5, 29), fontsize=15)

        cbar = fig.colorbar(image, ax=axes.ravel().tolist())
        cbar.set_label(self.config["cLabel"])
        return fig


def get_snaps_at_times(sim):
    times = [3.0 * pq.kyr, 32 * pq.kyr, 48 * pq.kyr]
    return [findSnapAtTime(sim, time) for time in times]


def findSnapAtTime(sim, time):
    return min(sim.snapshots, key=lambda snap: abs(snap.time - time))
