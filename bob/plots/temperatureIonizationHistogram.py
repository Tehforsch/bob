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
        super().__init__(config)
        self.config.setDefault("xUnit", pq.dimensionless_unscaled)
        self.config.setDefault("yUnit", pq.K)
        self.config.setDefault("xLabel", "$x_{\\mathrm{H}} [UNIT]$")
        self.config.setDefault("yLabel", "T [UNIT]")
        self.config.setDefault("minX", 1e-10)
        self.config.setDefault("maxX", 5e-0)
        self.config.setDefault("minY", 5e0)
        self.config.setDefault("maxY", 1e5)

    def post(self, sim: Simulation, snap: Snapshot) -> Result:
        return super().postHistogram(sim, snap, BasicField("ChemicalAbundances", 1), Temperature())

    def plot(self, plt: plt.axes, result: Result) -> None:
        plt.xticks([1e-10, 1e-8, 1e-6, 1e-4, 1e-2, 1e0])
        plt.yticks([1e0, 1e1, 1e2, 1e3, 1e4, 1e5])
        super().plot(plt, result)
