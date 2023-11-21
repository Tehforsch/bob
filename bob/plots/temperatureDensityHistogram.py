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


class TemperatureDensityHistogram(Histogram):
    def __init__(self, config: PlotConfig) -> None:
        config.setDefault("onlyIonized", False)
        filterStr = "_ionized" if config.get("onlyIonized") else ""
        config.setDefault("name", self.name + "_{simName}_{snapName}" + filterStr)
        super().__init__(config)
        self.config.setDefault("xUnit", pq.g / pq.cm**3)
        self.config.setDefault("yUnit", pq.K)
        self.config.setDefault("xLabel", "$\\rho [UNIT]$")
        self.config.setDefault("yLabel", "T [UNIT]")
        self.config.setDefault("minX", None)
        self.config.setDefault("maxX", None)
        self.config.setDefault("minY", None)
        self.config.setDefault("maxY", None)
        self.config.setDefault("xTicks", [1e-29, 1e-27, 1e-25, 1e-23])
        self.config.setDefault("yTicks", [1e2, 1e3, 1e4, 1e5, 1e6, 1e7])

    def post(self, sim: Simulation, snap: Snapshot) -> Result:
        return super().postHistogram(sim, snap, BasicField("Density"), Temperature())

    def plot(self, plt: plt.axes, result: Result) -> None:
        super().plot(plt, result)

    def filterFunction(self, snap):
        if self.config.get("onlyIonized"):
            hpAbundance = snap.ionized_hydrogen_fraction()
            indices = np.where(hpAbundance > 0.5)
            return indices
        else:
            return None
