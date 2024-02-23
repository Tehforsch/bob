import numpy as np
import matplotlib.pyplot as plt
import astropy.units as pq

from bob.simulation import Simulation
from bob.snapshot import Snapshot
from bob.result import Result
from bob.basicField import BasicField
from bob.plotConfig import PlotConfig
from bob.plots.histogram import Histogram


class DensityIonizationHistogram(Histogram):
    def __init__(self, config: PlotConfig) -> None:
        config.setDefault("name", self.name + "_{simName}_{snapName}")
        super().__init__(config)
        self.config.setDefault("xUnit", pq.g / pq.cm**3)
        self.config.setDefault("yUnit", pq.dimensionless_unscaled)
        self.config.setDefault("xLabel", "$\\rho [UNIT]$")
        self.config.setDefault("yLabel", "$x_{\\mathrm{HII}}$")
        self.config.setDefault("minX", None)
        self.config.setDefault("maxX", None)
        self.config.setDefault("minY", None)
        self.config.setDefault("maxY", None)
        self.config.setDefault("xTicks", None)
        self.config.setDefault("yTicks", None)

    def post(self, sim: Simulation, snap: Snapshot) -> Result:
        return super().postHistogram(sim, snap, BasicField("Density"), BasicField("ionized_hydrogen_fraction"))

    def plot(self, plt: plt.axes, result: Result) -> None:
        super().plot(plt, result)

    def filterFunction(self, snap):
        return None
