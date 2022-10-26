import matplotlib.pyplot as plt
import scipy
import numpy as np
import astropy.units as pq
from typing import Tuple, Any

from bob.simulationSet import SimulationSet
from bob.basicField import BasicField
from bob.result import Result
from bob.postprocessingFunctions import SetFn
from bob.plots.bobSlice import getSlice
from bob.plots.ionization import scaleFactorToAge, scaleFactorToRedshift
from bob.plotConfig import PlotConfig
import bob.config as config
from bob.util import isclose


class IonizationTime(SetFn):
    def __init__(self, config: PlotConfig) -> None:
        super().__init__(config)
        self.config.setDefault("xUnit", pq.Mpc)
        self.config.setDefault("yUnit", pq.Mpc)
        self.config.setDefault("xLabel", "$x [h^{-1} \\mathrm{UNIT}]$")
        self.config.setDefault("yLabel", "$y [h^{-1} \\mathrm{UNIT}]$")
        self.config.setDefault("velocity", False)  # Plot the velocity of the ionization front instead
        if self.config["velocity"]:
            self.config.setDefault("smoothingSigma", 0.0001 * pq.kpc)
            self.config.setDefault("vUnit", pq.cm / pq.s)
            self.config.setDefault("cLabel", "$v [\\mathrm{cm} / \mathrm{s}]$")
            self.config.setDefault("vLim", (0.0, 2e8))
            self.config.setDefault("name", self.config["name"].replace("ionizationTime", "ionizationVelocity"))
        else:
            self.config.setDefault("time", "z")
            if self.config["time"] == "z":
                self.config.setDefault("vUnit", pq.dimensionless_unscaled)
                self.config.setDefault("cLabel", "$z$")
                self.config.setDefault("vLim", (0.0, 20))
            else:
                self.config.setDefault("vUnit", pq.Myr)
                self.config.setDefault("cLabel", "$t [\\mathrm{Myr}]$")
                self.config.setDefault("vLim", (0.0, 2e2))

    def post(self, simSet: SimulationSet) -> Result:
        (extent, data) = self.getIonizationTimeData(simSet)
        result = Result()
        result.extent = list(extent)
        if self.config["velocity"]:
            if len(simSet) > 1:
                raise NotImplementedError("ionization velocity not implemented for multiple sims")
            snap = simSet[0].snapshots[-1]
            timeUnit = pq.s
            if (not isclose(snap.maxExtent[0], snap.maxExtent[1])) or (not isclose(snap.maxExtent[1], snap.maxExtent[2])):
                raise NotImplementedError("ionization velocity not implemented for non-cubic box")
            lengthUnit = snap.maxExtent[0] / config.dpi
            dataUnit = lengthUnit / timeUnit
            grad = np.gradient(data.to_value(timeUnit))
            result.data = 1.0 / (sum(np.abs(d) for d in grad))
            result.data[np.isnan(result.data)] = 0.0
            result.data[np.isinf(result.data)] = 0.0
            sigma = self.config["smoothingSigma"].to_value(lengthUnit)
            result.data = dataUnit * scipy.ndimage.gaussian_filter(result.data, sigma)
        else:
            result.data = data
        return result

    def plot(self, plt: plt.axes, result: Result) -> None:
        self.setupLabels()

        vmin, vmax = self.config["vLim"]
        self.image(result.data, result.extent, cmap="Reds", vmin=vmin, vmax=vmax)

    def getIonizationTimeData(self, simSet: SimulationSet) -> Tuple[Any, pq.Quantity]:
        if len(simSet) != 1:
            raise NotImplementedError("No implementation for multiple sims per set for ionizationTime")
        sim = simSet[0]
        if len(sim.snapshots) == 0:
            raise ValueError("No snapshots in sim")
        snap = sim.snapshots[-1]
        (extent, ionizationTime) = getSlice(BasicField("IonizationTime"), snap, "z", 0.5)
        if not self.config["velocity"] and self.config["time"] == "z":
            redshift = scaleFactorToRedshift(ionizationTime)
            return extent, redshift
        else:
            cosmology = sim.getCosmology()
            return extent, scaleFactorToAge(cosmology, ionizationTime)
            raise NotImplementedError("anything other than redshift not implemented - return age here?")
