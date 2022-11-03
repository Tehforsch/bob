from pathlib import Path
import astropy.units as pq
import astropy.cosmology.units as cu
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import cKDTree

from bob.util import getArrayQuantity
from bob.simulationSet import SimulationSet
from bob.result import Result
from bob.postprocessingFunctions import SetFn
from bob.plotConfig import PlotConfig
from bob.haloCatalog import GroupFiles
from bob.sourceField import SourceField
from bob.basicField import BasicField


class LuminosityOverHaloMass(SetFn):
    def __init__(self, config: PlotConfig) -> None:
        super().__init__(config)
        config.setDefault("xLabel", "$M_{\\mathrm{halo}} [M_{\\odot}]$")
        config.setDefault("yLabel", "$L_{\\star} [1/s]$")
        config.setDefault("xUnit", pq.Msun / cu.littleh)
        config.setDefault("yUnit", 1.0 / pq.s)
        config.setDefault("groupCatalogFolder", "groups")
        config.setDefault("numBins", 40)
        config.setDefault("redshift", 6.0)
        config.setDefault("postprocessing", True)
        config.setDefault("radiusFactor", 1.0)
        config.setDefault("scatter", False)
        config.setDefault("name", self.config["name"].replace("luminosityOverHaloMass", "luminosityOverHaloMassScatter"))

    def post(self, sims: SimulationSet) -> Result:
        files = GroupFiles(sims, Path(self.config["groupCatalogFolder"]))
        haloMasses = files.haloMasses()
        lengthUnit = pq.kpc / cu.littleh
        center_of_mass = files.center_of_mass().to(lengthUnit)
        radius = (files.halfmass_rad()).to(lengthUnit) * self.config["radiusFactor"]
        result = Result()
        assert len(sims) == 1, "Not implemented for more than one sim"
        sim = sims[0]
        if self.config["postprocessing"]:
            snap = sim.snapshots[-1]
        else:
            snap = sim.getSnapshotAtRedshift(self.config["redshift"])
        coords = BasicField("Coordinates", partType=0, comoving=True).getData(snap)
        sourceField = SourceField().getData(snap)
        tree = cKDTree(coords.to(lengthUnit, cu.with_H0(snap.H0)))
        luminosities = np.zeros(haloMasses.shape) / pq.s
        print(np.mean(sourceField), np.sum(sourceField))
        for (i, (pos, r)) in enumerate(zip(center_of_mass, radius)):
            indices = tree.query_ball_point(pos, r)
            luminosities[i] = np.sum(sourceField[indices])

        _, bins = np.histogram(haloMasses, bins=self.config["numBins"])
        if self.config["scatter"]:
            result.fullLuminosities = luminosities
            result.haloMasses = haloMasses
        else:  # histogram
            result.luminosity = []
            for (bstart, bend) in zip(bins, bins[1:]):
                indices = np.where((haloMasses >= bstart) & (haloMasses < bend))
                if len(luminosities) == 0:
                    result.luminosity.append(0.0 / pq.s)
                else:
                    result.luminosity.append(np.mean(luminosities[indices]))
            result.luminosity = getArrayQuantity(result.luminosity)
            result.bins = bins[1:]
        return result

    def plot(self, plt: plt.axes, result: Result) -> None:
        fig = plt.figure()
        ax = fig.add_subplot(2, 1, 1)
        if not self.config["scatter"]:
            self.setupLinePlot()
        self.setupLabels()
        ax.set_xscale("log")
        ax.set_yscale("log")
        if self.config["scatter"]:
            self.scatter(result.haloMasses, result.fullLuminosities)
        else:
            self.addLine(result.bins, result.luminosity)
