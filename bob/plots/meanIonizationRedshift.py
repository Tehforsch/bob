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
            for bstart, bend in zip(bins, bins[1:]):
                haloIndices = np.where((haloMasses >= bstart) & (haloMasses < bend))
                meanBins.append((bstart + bend) * 0.5)
                zs = []
                for i, (pos, r) in enumerate(zip(center_of_mass[haloIndices], radius[haloIndices])):
                    coordIndices = tree.query_ball_point(pos, r)
                    redshiftsThisHalo = ionizationRedshift[coordIndices]
                    redshiftsThisHalo = redshiftsThisHalo[np.where(redshiftsThisHalo < np.Inf)]
                    if redshiftsThisHalo.shape[0] > 0:
                        zs.append(np.mean(redshiftsThisHalo))
                meanZs.append(np.mean(np.array(zs)) * pq.dimensionless_unscaled)
            print(getArrayQuantity(meanZs))
            result.meanBins.append(getArrayQuantity(meanBins))
            result.meanZs.append(getArrayQuantity(meanZs))
        return result

    def plot(self, plt: plt.axes, result: Result) -> None:
        self.setupLinePlot()
        self.setupLabels()
        for meanBins, meanZs, label in zip(result.meanBins, result.meanZs, self.getLabels()):
            self.addLine(meanBins, meanZs, label=label)
