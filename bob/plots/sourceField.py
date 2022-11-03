import matplotlib.pyplot as plt
import scipy
import astropy.units as pq

from bob.simulation import Simulation
from bob.snapshot import Snapshot
from bob.result import Result
from bob.plots.bobSlice import Slice
from bob.plotConfig import PlotConfig


class SourceField(Slice):
    def __init__(self, config: PlotConfig) -> None:
        config.setDefault("field", "Sources")
        config.setDefault("testSources", False)
        config.setDefault("name", self.name + "_{simName}_{snapName}_{axis}")
        config.setDefault("colorByLuminosity", False)
        config.setDefault("sliceThickness", 0.02)
        config.setDefault("sigma", 1 * pq.kpc)
        super().__init__(config)

    def post(self, sim: Simulation, snap: Snapshot) -> Result:
        result = super().post(sim, snap)
        unit = result.data.unit
        coordUnit = (result.extent[1] - result.extent[0]) / result.data.shape[0]
        sigma = (self.config["sigma"] / coordUnit).to_value(1)
        result.data = unit * scipy.ndimage.gaussian_filter(result.data.to_value(unit), sigma)
        return result

    def plot(self, plt: plt.axes, result: Result) -> None:
        fig = super().plot(plt, result)
        super().showTimeIfDesired(fig, result)
