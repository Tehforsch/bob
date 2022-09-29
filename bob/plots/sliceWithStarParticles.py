import numpy as np
import matplotlib.pyplot as plt
import logging

from bob.simulation import Simulation
from bob.snapshot import Snapshot
from bob.result import Result
from bob.plots.bobSlice import Slice, findOrthogonalAxes, getAxisByName
from bob.plotConfig import PlotConfig


class SliceWithStarParticles(Slice):
    def __init__(self, config: PlotConfig) -> None:
        super().__init__(config)
        self.config.setDefault("testSources", True)
        self.config.setDefault("colorByLuminosity", False)
        self.config.setDefault("sliceThickness", 0.02)

    def post(self, sim: Simulation, snap: Snapshot) -> Result:
        result = super().post(sim, snap)
        f = snap.hdf5File
        if self.config["testSources"]:
            sources = sim.sources()
            coords = sources.coord * sim.snapshots[0].lengthUnit
            rates = sources.get136IonisationRate(sim)
        else:
            if "PartType4" in f:
                coords = snap.hdf5File["PartType4"]["Coordinates"] * snap.lengthUnit
                # times = np.array(f["PartType4"]["GFM_StellarFormationTime"])
                # coords = coords[np.where(times >= 0)]  # Filter out wind particles
                if self.config["colorByLuminosity"]:
                    raise NotImplementedError("Luminosity calculation not implemented for star particles yet")
            else:
                result.coords1 = np.zeros(()) * snap.lengthUnit
                result.coords2 = np.zeros(()) * snap.lengthUnit
                return result
        axis = getAxisByName(self.config["axis"])
        axis1, axis2 = findOrthogonalAxes(axis)
        extent = np.dot(snap.maxExtent - snap.minExtent, axis)
        relativeDist = np.abs((np.dot(coords, axis) / extent) - self.config["relativePosition"])
        indices = np.where(relativeDist < self.config["sliceThickness"])
        result.coords1 = np.dot(coords[indices].value, axis1) * coords.unit
        result.coords2 = np.dot(coords[indices].value, axis2) * coords.unit
        if self.config["colorByLuminosity"]:
            result.rates = rates[indices]
        return result

    def plot(self, plt: plt.axes, result: Result) -> None:
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        super().plot(ax, result)
        if len(result.coords1.shape) > 0:
            logging.debug(f"num stars: {result.coords1.shape[0]}")
            params = {}
            if self.config["colorByLuminosity"]:
                params["c"] = result.rates
                params["cmap"] = "Blues"
            self.scatter(result.coords1, result.coords2, **params)
