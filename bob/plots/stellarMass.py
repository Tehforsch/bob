from pathlib import Path
import astropy.units as pq
import astropy.cosmology.units as cu
import matplotlib.pyplot as plt
import numpy as np

from bob.util import getArrayQuantity
from bob.simulationSet import SimulationSet
from bob.result import Result
from bob.postprocessingFunctions import SetFn
from bob.plotConfig import PlotConfig
from bob.haloCatalog import GroupFiles


class StellarMass(SetFn):
    def __init__(self, config: PlotConfig) -> None:
        super().__init__(config)
        config.setDefault("xLabel", "$M_{\\mathrm{halo}}$")
        config.setDefault("yLabel", "$M_{\star}$")
        config.setDefault("xUnit", pq.Msun / cu.littleh)
        config.setDefault("yUnit", pq.Msun / cu.littleh)
        config.setDefault("groupCatalogFolder", "groups")
        config.setDefault("numBins", 40)

    def post(self, sims: SimulationSet) -> Result:
        files = GroupFiles(sims, Path(self.config["groupCatalogFolder"]))
        haloMasses = files.haloMasses()
        stellarMasses = files.stellarMasses()
        result = Result()
        _, bins = np.histogram(haloMasses, bins=self.config["numBins"])
        print(bins)

        result.meanBins = []
        result.stellarMasses = []
        for bstart, bend in zip(bins, bins[1:]):
            indices = np.where((haloMasses >= bstart) & (haloMasses < bend))
            stellarMass = np.mean(stellarMasses[indices])
            result.meanBins.append((bstart + bend) * 0.5)
            result.stellarMasses.append(stellarMass)
        result.meanBins = getArrayQuantity(result.meanBins)
        result.stellarMasses = getArrayQuantity(result.stellarMasses)
        return result

    def plot(self, plt: plt.axes, result: Result) -> None:
        fig = plt.figure()
        ax = fig.add_subplot(2, 1, 1)
        self.setupLinePlot()
        self.setupLabels()
        ax.set_xscale("log")
        ax.set_yscale("log")
        self.addLine(result.meanBins, result.stellarMasses)
