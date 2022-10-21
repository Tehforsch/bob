import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import astropy.units as pq

from bob.simulation import Simulation
from bob.snapshot import Snapshot
from bob.postprocessingFunctions import SnapFn
from bob.result import Result
from bob.basicField import BasicField
from bob.temperature import Temperature
from bob.plotConfig import PlotConfig


class TemperatureDensityHistogram(SnapFn):
    def __init__(self, config: PlotConfig) -> None:
        super().__init__(config)
        self.config.setDefault("only_ionized", False)
        self.config.setDefault("xUnit", "g / cm^3")
        self.config.setDefault("yUnit", "K")
        self.config.setDefault("xLabel", "$\\rho [UNIT]$")
        self.config.setDefault("yLabel", "T [UNIT]")
        ionizedStr = "_only_ionized" if self.config["only_ionized"] else ""
        self.config.setDefault("name", self.config["name"] + f"{ionizedStr}")
        self.config.setDefault("minX", 1e-31)
        self.config.setDefault("maxX", 5e-26)
        self.config.setDefault("minY", 5e0)
        self.config.setDefault("maxY", 2e6)
        self.config.setDefault("densityUnit", pq.g / pq.cm**3)

    def post(self, sim: Simulation, snap: Snapshot) -> Result:
        result = super().post(sim, snap)
        temperature = Temperature().getData(snap) / pq.K
        density = BasicField("Density").getData(snap) / self.config["densityUnit"]
        if self.config["only_ionized"]:
            hpAbundance = BasicField("ChemicalAbundances", 1).getData(snap)
            indices = np.where(hpAbundance > 0.5)
            temperature = temperature[indices]
            density = density[indices]
        minX, minY, maxX, maxY = self.config["minX"], self.config["minY"], self.config["maxX"], self.config["maxY"]
        binsX = np.logspace(np.log10(minX), np.log10(maxX), num=104)
        binsY = np.logspace(np.log10(minY), np.log10(maxY), num=104)
        print(np.min(temperature), np.mean(temperature), np.max(temperature))
        print(np.min(density), np.mean(density), np.max(density))
        result.H, result.x_edges, result.y_edges = np.histogram2d(density, temperature, bins=(binsX, binsY), density=True)
        result.H = result.H * pq.dimensionless_unscaled
        result.x_edges = result.x_edges * pq.dimensionless_unscaled
        result.y_edges = result.y_edges * pq.dimensionless_unscaled
        return result

    def plot(self, plt: plt.axes, result: Result) -> None:
        super().plot(plt, result)
        fig = plt.figure()
        ax = fig.add_subplot(2, 1, 1)
        self.setupLabels()
        ax.set_xscale("log")
        ax.set_yscale("log")
        plt.xticks([1e-31, 1e-30, 1e-29, 1e-28, 1e-27, 1e-26])
        plt.yticks([1e0, 1e1, 1e2, 1e3, 1e4, 1e5, 1e6, 1e7])
        X, Y = np.meshgrid(result.x_edges, result.y_edges)
        plt.pcolormesh(X, Y, result.H)
        plt.colorbar()
        # colorbar.set_ticks([1e17, 1e22, 1e27])
