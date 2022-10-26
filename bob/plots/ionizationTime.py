import matplotlib.pyplot as plt
import scipy
import numpy as np
import astropy.units as pq

from bob.simulationSet import SimulationSet
from bob.basicField import BasicField
from bob.result import Result
from bob.postprocessingFunctions import SetFn
from bob.plots.bobSlice import getSlice
from bob.plotConfig import PlotConfig
import bob.config as config
from bob.util import isclose
from bob.timeUtils import TimeQuantity


def toCoarserGrid(velData: pq.Quantity, factor: int) -> pq.Quantity:
    # shamelessly adapted from https://stackoverflow.com/questions/34689519/how-to-coarser-the-2-d-array-data-resolution
    temp = velData.reshape((velData.shape[0] // factor, factor, velData.shape[1] // factor, factor))
    return np.sum(temp, axis=(1, 3))


class IonizationTime(SetFn):
    def __init__(self, config: PlotConfig) -> None:
        super().__init__(config)
        self.config.setDefault("xUnit", pq.Mpc)
        self.config.setDefault("yUnit", pq.Mpc)
        self.config.setDefault("xLabel", "$x [h^{-1} \\mathrm{UNIT}]$")
        self.config.setDefault("yLabel", "$y [h^{-1} \\mathrm{UNIT}]$")
        self.config.setDefault("velocity", False)  # Plot the velocity of the ionization front instead
        self.config.setDefault("time", "z")
        self.config.setDefault("axis", "z")
        if self.config["velocity"]:
            self.config.setDefault("smoothingSigma", 0.0)
            self.config.setDefault("coarseness", 20)
            self.config.setDefault("velUnit", pq.cm / pq.s)
        if self.config["time"] == "z":
            self.config.setDefault("vUnit", pq.dimensionless_unscaled)
            self.config.setDefault("cLabel", "$z$")
            self.config.setDefault("vLim", (0.0, 20))
        else:
            self.config.setDefault("vUnit", pq.Myr)
            self.config.setDefault("cLabel", "$t [\\mathrm{Myr}]$")
            self.config.setDefault("vLim", (0.0, 2e2))

    def post(self, simSet: SimulationSet) -> Result:
        result = self.getIonizationTimeData(simSet)
        if self.config["velocity"]:
            if len(simSet) > 1:
                raise NotImplementedError("ionization velocity not implemented for multiple sims")
            snap = simSet[0].snapshots[-1]
            timeUnit = pq.s
            if (not isclose(snap.maxExtent[0], snap.maxExtent[1])) or (not isclose(snap.maxExtent[1], snap.maxExtent[2])):
                raise NotImplementedError("ionization velocity not implemented for non-cubic box")
            lengthUnit = snap.maxExtent[0] / config.dpi
            dataUnit = lengthUnit / timeUnit
            grad = np.gradient(result.time.to_value(timeUnit))
            result.velX = 1.0 / grad[0]
            result.velY = 1.0 / grad[1]
            result.velX[np.isnan(result.velX)] = 0.0
            result.velY[np.isnan(result.velY)] = 0.0
            result.velX[np.isinf(result.velX)] = 0.0
            result.velY[np.isinf(result.velY)] = 0.0
            result.velX = toCoarserGrid(result.velX, self.config["coarseness"])
            result.velY = toCoarserGrid(result.velY, self.config["coarseness"])
            sigma = self.config["smoothingSigma"]
            result.velX = dataUnit * scipy.ndimage.gaussian_filter(result.velX, sigma)
            result.velY = dataUnit * scipy.ndimage.gaussian_filter(result.velY, sigma)
            print(np.mean(result.velX))
        return result

    def plot(self, plt: plt.axes, result: Result) -> None:
        self.setupLabels()
        fig, ax = plt.subplots(1, 1)
        vmin, vmax = self.config["vLim"]
        # Dont know why exactly but if we dont flip this, the results are in the wrong position
        result.showTime = np.flip(result.showTime, axis=0)
        self.image(ax, result.showTime, result.extent, cmap="Reds", vmin=vmin, vmax=vmax)
        if self.config["velocity"]:
            (xlen, ylen) = result.showTime.shape
            xUnit = self.config["xUnit"]
            yUnit = self.config["yUnit"]
            X, Y = np.meshgrid(
                np.linspace(result.extent[0].to_value(xUnit), result.extent[1].to_value(xUnit), xlen // self.config["coarseness"]),
                np.linspace(result.extent[2].to_value(yUnit), result.extent[3].to_value(yUnit), ylen // self.config["coarseness"]),
            )

            ax.quiver(
                X,
                Y,
                result.velY.to_value(self.config["velUnit"]),
                result.velX.to_value(self.config["velUnit"]),
            )

    def getIonizationTimeData(self, simSet: SimulationSet) -> Result:
        if len(simSet) != 1:
            raise NotImplementedError("No implementation for multiple sims per set for ionizationTime")
        sim = simSet[0]
        if len(sim.snapshots) == 0:
            raise ValueError("No snapshots in sim")
        snap = sim.snapshots[-1]
        (extent, ionizationTime) = getSlice(BasicField("IonizationTime"), snap, self.config["axis"], 0.5)
        result = Result()
        result.extent = list(extent)
        ionizationTime = TimeQuantity(sim, ionizationTime)
        if self.config["time"] == "z":
            result.showTime = ionizationTime.redshift()
        else:
            result.showTime = ionizationTime.time()
        if self.config["velocity"]:
            if sim.simType().is_cosmological():
                result.time = ionizationTime.age()
            else:
                result.time = ionizationTime.time()
        return result
