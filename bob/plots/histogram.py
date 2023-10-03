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

    def postHistogram(self, sim: Simulation, snap: Snapshot, fieldX: Field, fieldY: Field) -> Result:
        result = super().post(sim, snap)
        dataX = fieldX.getData(snap).to_value(self.config["xUnit"], cu.with_H0(snap.H0))
        dataY = fieldY.getData(snap).to_value(self.config["yUnit"], cu.with_H0(snap.H0))
        indices = self.filterFunction(snap)
        if indices is not None:
            dataX = dataX[indices]
            dataY = dataY[indices]
        minX, minY, maxX, maxY = self.config["minX"], self.config["minY"], self.config["maxX"], self.config["maxY"]
        binsX = np.logspace(np.log10(minX), np.log10(maxX), num=104)
        binsY = np.logspace(np.log10(minY), np.log10(maxY), num=104)
        print(np.min(dataX), np.mean(dataX), np.max(dataX))
        print(np.min(dataY), np.mean(dataY), np.max(dataY))
        result.H, result.x_edges, result.y_edges = np.histogram2d(dataX, dataY, bins=(binsX, binsY), density=True)
        result.H = result.H.T * pq.dimensionless_unscaled
        result.x_edges = result.x_edges * pq.dimensionless_unscaled
        result.y_edges = result.y_edges * pq.dimensionless_unscaled
        return result

    def plot(self, plt: plt.axes, result: Result) -> None:
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        self.setupLabels()
        ax.set_xscale("log")
        ax.set_yscale("log")
        super().showTimeIfDesired(fig, result)
        X, Y = np.meshgrid(result.x_edges, result.y_edges)
        plt.pcolormesh(X, Y, result.H, norm=colors.LogNorm())
        plt.colorbar()
        if self.config["xTicks"] is not []:
            plt.xticks(self.config["xTicks"])
        if self.config["yTicks"] is not []:
            plt.yticks(self.config["yTicks"])
        super().plot(plt, result)

    def filterFunction(self, snap):
        return None
