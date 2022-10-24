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
        config.setDefault("xLabel", "$M_{\\mathrm{halo}}$")
        config.setDefault("yLabel", "$L_{\star}$")
        config.setDefault("xUnit", pq.Msun / cu.littleh)
        config.setDefault("yUnit", 1.0 / pq.s)
        config.setDefault("groupCatalogFolder", "groups")
        config.setDefault("numBins", 40)
        config.setDefault("redshift", 6.0)
        config.setDefault("postprocessing", True)

    def post(self, sims: SimulationSet) -> Result:
        files = GroupFiles(sims, Path(self.config["groupCatalogFolder"]))
        haloMasses = files.haloMasses()
        center_of_mass = files.center_of_mass()
        radius = files.r_crit200()
        result = Result()
        _, bins = np.histogram(haloMasses, bins=self.config["numBins"])

        result.luminosity = []

        assert len(sims) == 1, "Not implemented for more than one sim"
        sim = sims[0]
        if self.config["postprocessing"]:
            snap = sim.snapshots[-1]
        else:
            snap = sim.getSnapshotAtRedshift(self.config["redshift"])
        coords = BasicField("Coordinates", partType=0, comoving=True).getData(snap)
        sourceField = SourceField(sim).getData(snap)
        lengthUnit = pq.kpc / cu.littleh
        tree = cKDTree(coords.to(lengthUnit, cu.with_H0(snap.H0)))

        for (bstart, bend) in zip(bins, bins[1:]):
            indices = np.where((haloMasses >= bstart) & (haloMasses < bend))
            com = center_of_mass[indices].to(lengthUnit)
            radii = radius[indices].to(lengthUnit)
            luminosities = np.zeros(radii.shape) / pq.s
            for (i, (pos, r)) in enumerate(zip(com, radii)):
                indices = tree.query_ball_point(pos, r)
                luminosities[i] = np.sum(sourceField[indices])
            if len(luminosities) == 0:
                result.luminosity.append(0.0 / pq.s)
            else:
                result.luminosity.append(np.mean(luminosities))
        result.bins = getArrayQuantity(bins[1:])
        result.luminosity = getArrayQuantity(result.luminosity)
        print(getArrayQuantity(result.luminosity))
        return result

    def plot(self, plt: plt.axes, result: Result) -> None:
        fig = plt.figure()
        ax = fig.add_subplot(2, 1, 1)
        self.setupLinePlot()
        self.setupLabels()
        ax.set_xscale("log")
        ax.set_yscale("log")
        self.addLine(result.bins, result.luminosity)
