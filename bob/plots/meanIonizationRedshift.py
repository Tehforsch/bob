from pathlib import Path
import astropy.units as pq
import astropy.cosmology.units as cu
import matplotlib.pyplot as plt
import numpy as np

from scipy.spatial import cKDTree
from bob.util import getArrayQuantity
from bob.result import Result
from bob.postprocessingFunctions import MultiSetFn
from bob.multiSet import MultiSet
from bob.plotConfig import PlotConfig
from bob.haloCatalog import GroupFiles
from bob.basicField import BasicField
from bob.timeUtils import TimeQuantity


class MeanIonizationRedshift(MultiSetFn):
    def __init__(self, config: PlotConfig) -> None:
        super().__init__(config)
        config.setDefault("xLabel", "$M_{\\mathrm{halo}}$")
        config.setDefault("yLabel", "$z$")
        config.setDefault("xUnit", pq.Msun / cu.littleh)
        config.setDefault("yUnit", pq.dimensionless_unscaled)
        config.setDefault("groupCatalogFolder", "groups")
        config.setDefault("numBins", 5)
        config.setDefault("radiusFactor", 10.0)

    def post(self, simSet: MultiSet) -> Result:
        result = Result()
        result.meanBins = []
        result.meanZs = []
        lengthUnit = pq.kpc / cu.littleh
        for sims in simSet:
            print(sims)
            files = GroupFiles(sims, Path(self.config["groupCatalogFolder"]))
            haloMasses = files.haloMasses()
            assert len(sims) == 1
            sim = sims[0]
            snap = sim.snapshots[-1]
            coords = BasicField("Coordinates", partType=0, comoving=True).getData(snap)
            center_of_mass = files.center_of_mass().to(lengthUnit)
            radius = (files.halfmass_rad()).to(lengthUnit) * self.config["radiusFactor"]
            tree = cKDTree(coords.to(lengthUnit, cu.with_H0(snap.H0)))
            ionizationTime = BasicField("IonizationTime").getData(snap)
            ionizationRedshift = TimeQuantity(sim, ionizationTime).redshift()
            _, bins = np.histogram(haloMasses, bins=self.config["numBins"])
            meanBins = []
            meanZs = []
            for (bstart, bend) in zip(bins, bins[1:]):
                indices = np.where((haloMasses >= bstart) & (haloMasses < bend))
                meanBins.append((bstart + bend) * 0.5)
                z = np.zeros(haloMasses.shape) * pq.dimensionless_unscaled
                for (i, (pos, r)) in enumerate(zip(center_of_mass, radius)):
                    indices = tree.query_ball_point(pos, r)
                    z[i] = np.mean(ionizationRedshift[indices])
                z = np.mean(z)
                meanZs.append(z)
            result.meanBins.append(getArrayQuantity(meanBins))
            result.meanZs.append(getArrayQuantity(meanZs))
        return result

    def plot(self, plt: plt.axes, result: Result) -> None:
        fig = plt.figure()
        ax = fig.add_subplot(2, 1, 1)
        self.setupLinePlot()
        self.setupLabels()
        ax.set_xscale("log")
        ax.set_yscale("log")
        for (meanBins, meanZs) in zip(result.meanBins, result.meanZs):
            self.addLine(result.meanBins, result.meanZs)
