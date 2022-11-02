import numpy as np
import matplotlib.pyplot as plt
import astropy.units as pq

from bob.result import Result
from bob.basicField import BasicField
from bob.plotConfig import PlotConfig
from bob.util import getArrayQuantity
from bob.postprocessingFunctions import SetFn
from bob.simulationSet import SimulationSet
from bob.snapshotFilter import SnapshotFilter
from bob.volume import Volume


class IonizationLevel(SetFn):
    def __init__(self, config: PlotConfig) -> None:
        super().__init__(config)
        self.config.setDefault("minX", 1e-5)
        self.config.setDefault("maxX", 1e-1)
        self.config.setDefault("numBins", 50)
        self.config.setDefault("snapshots", None)
        self.config.setDefault("xLabel", "$x_{\\mathrm{V}}$")
        self.config.setDefault("yLabel", "$f(x_{\\mathrm{V}}) x_{\\mathrm{V}}$")
        self.config.setDefault("xUnit", pq.dimensionless_unscaled)
        self.config.setDefault("yUnit", pq.dimensionless_unscaled)

    def ylabel(self) -> str:
        return "$x_{\\mathrm{H+}}$"

    def post(self, sims: SimulationSet) -> Result:
        result = Result()
        minX = self.config["minX"]
        maxX = self.config["maxX"]
        binsX = np.logspace(np.log10(minX), np.log10(maxX), num=self.config["numBins"] + 1)
        result.bins = binsX * pq.dimensionless_unscaled
        result.volumeFraction = []
        for sim in sims:
            snapshots = SnapshotFilter(self.config["snapshots"]).get_snapshots(sim)
            for snap in snapshots:
                volumes = Volume(comoving=True).getData(snap)
                totalVolume = np.sum(volumes)
                ionization = BasicField("ChemicalAbundances", 1).getData(snap)
                volumeFraction = []
                for (bMin, bMax) in zip(binsX, binsX[1:]):
                    indices = np.where((bMin <= ionization) & (ionization < bMax))
                    volumeFraction.append(np.sum(volumes[indices]) / totalVolume)
                result.volumeFraction.append(getArrayQuantity(volumeFraction) * np.diff(binsX))
        return result

    def plot(self, plt: plt.axes, result: Result) -> None:
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        self.setupLinePlot(ax)
        ax.set_xscale("log")
        ax.set_yscale("log")
        for volumeFraction in result.volumeFraction:
            self.addLine(result.bins[1:], volumeFraction, label="")
