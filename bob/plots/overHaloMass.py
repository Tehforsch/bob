from abc import abstractmethod
from pathlib import Path
import astropy.units as pq
import astropy.cosmology.units as cu
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import cKDTree
import tqdm

from bob.util import getArrayQuantity
from bob.simulationSet import SimulationSet
from bob.result import Result
from bob.postprocessingFunctions import SetFn
from bob.plotConfig import PlotConfig
from bob.haloCatalog import GroupFiles
from bob.basicField import BasicField
from bob.snapshot import Snapshot


class OverHaloMass(SetFn):
    def __init__(self, config: PlotConfig) -> None:
        config.setDefault("stellarMass", False)  # plot function of the stellar mass instead
        if config["stellarMass"]:
            config.setDefault("xLabel", "$M_{\\star} [M_{\\odot}]$")
        else:
            config.setDefault("xLabel", "$M_{\\mathrm{halo}} [M_{\\odot}]$")
        config.setDefault("xUnit", pq.Msun / cu.littleh)
        config.setDefault("groupCatalogFolder", "groups")
        config.setDefault("numBins", 40)
        config.setDefault("redshift", 6.0)
        config.setDefault("postprocessing", True)
        config.setDefault("radiusFactor", 1.0)
        config.setDefault("scatter", False)
        config.setDefault("median", False)
        config.setDefault("showTime", True)
        config.setDefault("time", "z")
        config.setDefault("timeUnit", pq.dimensionless_unscaled)
        config.setDefault("statistic", "mean")
        super().__init__(config)

    @abstractmethod
    def quantity(self, snap: Snapshot) -> pq.Quantity:
        pass

    def evaluateQuantityForHalo(self, tree: cKDTree, quantity: pq.Quantity, pos: pq.Quantity, r: pq.Quantity) -> pq.Quantity:
        indices = tree.query_ball_point(pos, r)
        statistic = self.config["statistic"]
        if statistic == "sum":
            return np.sum(quantity[indices])
        elif statistic == "mean":
            return np.mean(quantity[indices])
        else:
            raise ValueError("Unknown statistic f{statistic}")

    def post(self, sims: SimulationSet) -> Result:
        files = GroupFiles(sims, Path(self.config["groupCatalogFolder"]))
        if self.config["stellarMass"]:
            masses = files.stellarMasses()
        else:
            masses = files.haloMasses()
        lengthUnit = pq.kpc
        result = Result()
        assert len(sims) == 1, "Not implemented for more than one sim"
        sim = sims[0]
        if self.config["postprocessing"]:
            snap = sim.snapshots[-1]
        else:
            snap = sim.getSnapshotAtRedshift(self.config["redshift"])
        result.time = snap.timeQuantity(self.config["time"])
        center_of_mass = files.center_of_mass().to(lengthUnit, cu.with_H0(snap.H0))
        radius = (files.halfmass_rad()).to(lengthUnit, cu.with_H0(snap.H0)) * self.config["radiusFactor"]
        coords = BasicField("Coordinates", partType=0, comoving=True).getData(snap)
        tree = cKDTree(coords.to(lengthUnit, cu.with_H0(snap.H0)))
        quantity = self.quantity(snap)
        values = np.zeros(masses.shape) * self.config["yUnit"]
        numHaloes = center_of_mass.shape[0]
        for i in tqdm.trange(numHaloes):
            pos = center_of_mass[i]
            r = radius[i]
            values[i] = self.evaluateQuantityForHalo(tree, quantity, pos.to(lengthUnit, cu.with_H0(snap.H0)), r)

        _, bins = np.histogram(masses, bins=self.config["numBins"])
        if self.config["scatter"]:
            result.fullValues = values
            result.masses = masses
        else:  # histogram
            result.values = []
            for (bstart, bend) in zip(bins, bins[1:]):
                indices = np.where((masses >= bstart) & (masses < bend))
                if len(values) == 0:
                    result.values.append(0.0 / pq.s)
                else:
                    if self.config["median"]:
                        result.values.append(np.median(values[indices]))
                    else:
                        result.values.append(np.mean(values[indices]))
            result.values = getArrayQuantity(result.values)
            result.bins = bins[1:]
        return result

    def plot(self, plt: plt.axes, result: Result) -> None:
        fig = plt.figure()
        ax = fig.add_subplot(2, 1, 1)
        self.showTimeIfDesired(fig, result)
        if not self.config["scatter"]:
            self.setupLinePlot()
        self.setupLabels()
        ax.set_xscale("log")
        ax.set_yscale("log")
        if self.config["scatter"]:
            self.scatter(result.masses, result.fullValues)
        else:
            self.addLine(result.bins, result.values)
