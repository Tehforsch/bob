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


class TemperatureRateHistogram(Histogram):
    def __init__(self, config: PlotConfig) -> None:
        config.setDefault("field", "recombination_rate")
        config.setDefault("name", "temperature_{field}_{simName}_{snapName}")
        super().__init__(config)
        self.config.setDefault("xUnit", 1 / pq.s)
        self.config.setDefault("yUnit", pq.K)
        self.config.setDefault("xLabel", "rate")
        self.config.setDefault("yLabel", "T [UNIT]")
        self.config.setDefault("minX", None)
        self.config.setDefault("maxX", None)
        self.config.setDefault("minY", None)
        self.config.setDefault("maxY", None)
        self.config.setDefault("xTicks", None)
        self.config.setDefault("yTicks", None)

    def post(self, sim: Simulation, snap: Snapshot) -> Result:
        return super().postHistogram(sim, snap, BasicField(self.config["field"]), Temperature())

    def plot(self, plt: plt.axes, result: Result) -> None:
        super().plot(plt, result)

    def filterFunction(self, snap):
        return None
