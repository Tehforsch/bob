import matplotlib.gridspec as gridspec
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import astropy.units as pq
import astropy.cosmology.units as cu

from bob.simulation import Simulation
from bob.snapshot import Snapshot
from bob.postprocessingFunctions import SnapFn
from bob.result import Result
from bob.basicField import BasicField
from bob.plotConfig import PlotConfig
from bob.field import Field


class Histogram(SnapFn):
    def __init__(self, config: PlotConfig) -> None:
        super().__init__(config)
        self.config.setDefault("empty", False)

    def postHistogram(self, sim: Simulation, snap: Snapshot, fieldX: Field, fieldY: Field) -> Result:
        result = super().post(sim, snap)
        print(fieldX, fieldY)
        dataX = fieldX.getData(snap).to_value(self.config["xUnit"], cu.with_H0(snap.H0))
        dataY = fieldY.getData(snap).to_value(self.config["yUnit"], cu.with_H0(snap.H0))
        print(self.config["yUnit"])
        indices = self.filterFunction(snap)
        if indices is not None:
            dataX = dataX[indices]
            dataY = dataY[indices]
            if indices[0].shape[0] == 0:
                print("Empty plot due to filter settings!")
                self.config["empty"] = True
        if self.config["minX"] is not None:
            minX, minY, maxX, maxY = self.config["minX"], self.config["minY"], self.config["maxX"], self.config["maxY"]
        else:
            minX, minY, maxX, maxY = np.min(dataX), np.min(dataY), np.max(dataX), np.max(dataY)
        binsX = np.logspace(np.log10(minX), np.log10(maxX), num=104)
        binsY = np.logspace(np.log10(minY), np.log10(maxY), num=104)
        if not self.config["empty"]:
            print(np.min(dataX), np.mean(dataX), np.max(dataX))
            print(np.min(dataY), np.mean(dataY), np.max(dataY))
        result.H, result.x_edges, result.y_edges = np.histogram2d(dataX, dataY, bins=(binsX, binsY))
        result.H = result.H.T * pq.dimensionless_unscaled
        result.x_edges = result.x_edges * pq.dimensionless_unscaled
        result.y_edges = result.y_edges * pq.dimensionless_unscaled
        return result

    def plot(self, plt: plt.axes, result: Result) -> None:
        fig = plt.figure(figsize=(6, 6))
        gs = fig.add_gridspec(2, 2, width_ratios=(4, 1), height_ratios=(1, 4), left=0.1, right=0.9, bottom=0.1, top=0.9, wspace=0.15, hspace=0.15)
        ax = fig.add_subplot(gs[1, 0])
        axx = fig.add_subplot(gs[0, 0], sharex=ax)
        axy = fig.add_subplot(gs[1, 1], sharey=ax)
        self.setupLabels(ax=ax)
        ax.set_xscale("log")
        ax.set_yscale("log")
        super().showTimeIfDesired(fig, result)
        X, Y = np.meshgrid(result.x_edges, result.y_edges)
        xDat = np.sum(result.H, axis=0)
        yDat = np.sum(result.H, axis=1)
        ax.pcolormesh(X, Y, result.H, norm=colors.LogNorm())
        # if not self.config["empty"]:
        # ax.set_colorbar()
        if self.config["xTicks"] is not None:
            ax.xticks(self.config["xTicks"])
        if self.config["yTicks"] is not None:
            ax.yticks(self.config["yTicks"])

        xs = 0.5 * (np.diag(X)[1:] + np.diag(X)[0:-1])
        axx.plot(xs, xDat)
        # axx.set_xlim(ax.get_xlim())
        axx.set_xscale("log")
        axx.set_yscale("log")

        ys = 0.5 * (np.diag(Y)[1:] + np.diag(Y)[0:-1])
        axy.plot(yDat, ys)
        # axy.set_ylim(ax.get_ylim())
        axy.set_xscale("log")
        axy.set_yscale("log")
        super().plot(ax, result)

    def filterFunction(self, snap):
        return None
