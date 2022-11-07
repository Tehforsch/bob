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
        super().__init__(config)
        self.config.setDefault("xUnit", pq.g / pq.cm**3)
        self.config.setDefault("yUnit", pq.K)
        self.config.setDefault("xLabel", "$\\rho [UNIT]$")
        self.config.setDefault("yLabel", "T [UNIT]")
        self.config.setDefault("minX", 1e-31)
        self.config.setDefault("maxX", 5e-26)
        self.config.setDefault("minY", 5e0)
        self.config.setDefault("maxY", 2e6)

    def post(self, sim: Simulation, snap: Snapshot) -> Result:
        return super().postHistogram(sim, snap, BasicField("Density"), Temperature())

    def plot(self, plt: plt.axes, result: Result) -> None:
        super().plot(plt, result)
        plt.xticks([1e-31, 1e-30, 1e-29, 1e-28, 1e-27, 1e-26])
        plt.yticks([1e0, 1e1, 1e2, 1e3, 1e4, 1e5, 1e6, 1e7])
