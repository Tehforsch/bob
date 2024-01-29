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
from bob.subsweepSimulation import Cosmology


def toCoarserGrid(velData: pq.Quantity, factor: int) -> pq.Quantity:
    # shamelessly adapted from https://stackoverflow.com/questions/34689519/how-to-coarser-the-2-d-array-data-resolution
    temp = velData.reshape((velData.shape[0] // factor, factor, velData.shape[1] // factor, factor))
    return np.sum(temp, axis=(1, 3))


class IonizationTime(SetFn):
    def __init__(self, config: PlotConfig) -> None:
        super().__init__(config)
        self.config.setDefault("xUnit", pq.Mpc)
        self.config.setDefault("yUnit", pq.Mpc)
        self.config.setDefault("colorbar", True)
        self.config.setDefault("clabel", "z")
        self.config.setDefault("xLabel", "$x [h^{-1} \\mathrm{UNIT}]$")
        self.config.setDefault("yLabel", "$y [h^{-1} \\mathrm{UNIT}]$")
        self.config.setDefault("velocity", True)
        self.config.setDefault("time", "z")
        self.config.setDefault("axis", "z")
        if self.config["velocity"]:
            self.config.setDefault("smoothingSigma", 0.0)
            self.config.setDefault("coarseness", 20)
            self.config.setDefault("norm", False)
            if self.config["norm"]:
                self.config.setDefault("velUnit", pq.dimensionless_unscaled)
            else:
                self.config.setDefault("velUnit", pq.cm / pq.s)
        if self.config["time"] == "z":
            self.config.setDefault("vUnit", pq.dimensionless_unscaled)
            self.config.setDefault("cLabel", "$z$")
            self.config.setDefault("vLim", [0.0, 20])
        else:
            self.config.setDefault("vUnit", pq.Myr)
            self.config.setDefault("cLabel", "$t [\\mathrm{Myr}]$")
        self.config.setDefault("quotient", None)
        self.config.setDefault("minExtent", None)
        self.config.setDefault("maxExtent", None)

    def post(self, simSet: SimulationSet) -> Result:
        result = self.getIonizationTimeData(simSet)
        cosmology = simSet[0].cosmology()
        result.a = cosmology["a"] * pq.dimensionless_unscaled
        result.h = cosmology["h"] * pq.dimensionless_unscaled
        snap = simSet[0].snapshots[-1]
        with cosmology.unit_context():
            if self.config["velocity"]:
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
                sigma = pq.Quantity(self.config["smoothingSigma"]).to_value(lengthUnit)
                result.velX = dataUnit * scipy.ndimage.gaussian_filter(result.velX, sigma)
                result.velY = dataUnit * scipy.ndimage.gaussian_filter(result.velY, sigma)
                if self.config["norm"]:
                    norm = np.sqrt(result.velX**2 + result.velY**2)
                    result.velX = result.velX / norm
                    result.velY = result.velY / norm
        return result

    def plot(self, plt: plt.axes, result: Result) -> None:
        cosmology = Cosmology({"a": result.a.value, "h": result.h.value})
        with cosmology.unit_context():
            self.setupLabels()
            fig, ax = plt.subplots(1, 1)
            if "vLim" in self.config:
                vmin, vmax = self.config["vLim"]
            else:
                vmin, vmax = 0, np.max(result.redshift)
            # Dont know why exactly but if we dont flip this, the results are in the wrong position
            result.redshift = np.flip(result.redshift, axis=0)
            self.image(ax, result.redshift, result.extent, cmap="Reds", vmin=vmin, vmax=vmax, colorbar=self.config["colorbar"])
            if self.config["velocity"]:
                (xlen, ylen) = result.redshift.shape
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
        result = Result()
        extent = None
        for sim in simSet:
            (nextent, data) = self.getIonizationTimeDataForSim(sim)
            if extent is None:
                extent = nextent
            if "time" not in result.__dict__:
                result.time = data
            else:
                # only update the inf values
                mask = np.where(result.time == np.inf)
                result.time[mask] = data[mask]
            mask = np.where(result.time == np.inf)
            if result.time[mask].shape == (0,):
                print("No more infinity values. Done")
                break
        result.extent = list(extent)
        # result.time = ionizationTime
        result.redshift = ageToRedshift(result.time, sim)
        return result

    def getIonizationTimeDataForSim(self, sim) -> Result:
        if len(sim.snapshots) == 0:
            raise ValueError("No snapshots in sim")
        last_snap = sim.snapshots[-1]
        (extent, ionizationTime) = getSlice(BasicField("ionization_time"), last_snap, self.config["axis"], 0.5)
        return (extent, shiftBySimAge(ionizationTime, sim))


def shiftBySimAge(simTime, sim):
    from bob.timeUtils import redshiftToAge

    cosmology = sim.getCosmology()
    z = 1.0 / sim.cosmology()["a"] - 1.0
    age = redshiftToAge(cosmology, np.array([z]))
    time = age + simTime
    print("a", np.min(time).to_value(pq.Myr), np.max(time).to_value(pq.Myr))
    return time


def ageToRedshift(age, sim):
    from bob.timeUtils import ageToRedshift

    cosmology = sim.getCosmology()
    mask = np.where(age != np.inf)
    redshift = -np.ones(age.shape) * np.inf
    print(np.mean(age[mask]))
    print(np.mean(ageToRedshift(cosmology, age[mask])))
    redshift[mask] = ageToRedshift(cosmology, age[mask])
    return redshift * pq.dimensionless_unscaled
