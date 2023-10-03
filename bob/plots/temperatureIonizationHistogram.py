import numpy as np
import matplotlib.pyplot as plt
import astropy.units as pq

from bob.simulation import Simulation
from bob.snapshot import Snapshot
from bob.result import Result
from bob.basicField import BasicField
from bob.temperature import Temperature
from bob.plotConfig import PlotConfig
from bob.plots.histogram import Histogram


class TemperatureIonizationHistogram(Histogram):
    def __init__(self, config: PlotConfig) -> None:
        defaultFilter = [">", "0 g cm^-3"]
        config.setDefault("densityFilter", defaultFilter)
        (aboveOrBelow, threshold) = config["densityFilter"]
        filterStr = "_dens" + aboveOrBelow + "" + str(pq.Quantity(threshold).to_value(pq.g / pq.cm**3)) if config["densityFilter"] != defaultFilter else ""
        config.setDefault("name", self.name + "_{simName}_{snapName}" + filterStr)
        super().__init__(config)
        self.config.setDefault("xUnit", pq.dimensionless_unscaled)
        self.config.setDefault("yUnit", pq.K)
        self.config.setDefault("xLabel", "$x_{\\mathrm{HII}} [UNIT]$")
        self.config.setDefault("yLabel", "T [UNIT]")
        self.config.setDefault("minX", 1e-10)
        self.config.setDefault("maxX", 5e-0)
        self.config.setDefault("minY", 5e0)
        self.config.setDefault("maxY", 1e5)
        self.config.setDefault("xTicks", [1e-10, 1e-8, 1e-6, 1e-4, 1e-2, 1e0])
        self.config.setDefault("yTicks", [1e0, 1e1, 1e2, 1e3, 1e4, 1e5])

    def post(self, sim: Simulation, snap: Snapshot) -> Result:
        return super().postHistogram(sim, snap, BasicField("ChemicalAbundances", 1), Temperature())

    def plot(self, plt: plt.axes, result: Result) -> None:
        super().plot(plt, result)

    def filterFunction(self, snap):
        densityFilter = self.config.get("densityFilter")
        if densityFilter[0] == ">":
            above = True
        elif densityFilter[0] == "<":
            above = False
        else:
            raise ValueError(densityFilter[0])
        densityThreshold = pq.Quantity(densityFilter[1])
        dens = snap.density().to_value(densityThreshold.unit)
        if above:
            return np.where(dens > densityThreshold.value)
        else:
            return np.where(dens < densityThreshold)
