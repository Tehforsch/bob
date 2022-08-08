import numpy as np
import matplotlib.pyplot as plt

from bob.simulation import Simulation
from bob.snapshot import Snapshot
from bob.result import Result
from bob.plots.bobSlice import Slice
from bob.plotConfig import PlotConfig


class SliceWithStarParticles(Slice):
    def __init__(self, config: PlotConfig) -> None:
        super().__init__(config)
        self.config.setDefault("circleSize", 0.05)
        self.config.setDefault("testSources", True)
        self.config.setDefault("colorByLuminosity", False)

    def post(self, sim: Simulation, snap: Snapshot) -> Result:
        result = super().post(sim, snap)
        f = snap.hdf5File
        centerZ = snap.center[2]
        extentZ = (snap.maxExtent - snap.minExtent)[2]
        if self.config["testSources"]:
            sources = sim.sources()
            print(sources)
            coords = sources.coord * sim.snapshots[0].lengthUnit
            rates = sources.get136IonisationRate(sim)
        else:
            if "PartType4" in f:
                coords = snap.hdf5File["PartType4"]["Coordinates"] * snap.lengthUnit
                times = np.array(f["PartType4"]["GFM_StellarFormationTime"])
                coords = coords[np.where(times >= 0)]  # Filter out wind particles
                if self.config["colorByLuminosity"]:
                    raise NotImplementedError("Luminosity calculation not implemented for star particles yet")
            else:
                result.coords = np.zeros(()) * snap.lengthUnit
                return result
        zRelativeDist = np.abs((coords[:, 2] - centerZ) / extentZ)
        result.coords = coords[np.where(zRelativeDist < 0.02)]
        if self.config["colorByLuminosity"]:
            result.rates = rates[np.where(zRelativeDist < 0.02)]
        return result

    def plot(self, plt: plt.axes, result: Result) -> None:
        if self.config["axis"] != "z":
            raise NotImplementedError("Implement other axes by adjusting the coordinates below")
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        super().plot(ax, result)
        if len(result.coords.shape) > 0:
            print(f"num stars: {result.coords.shape[0]}")
            params = {}
            if self.config["colorByLuminosity"]:
                print(result.rates)
                params["c"] = result.rates
            self.scatter(result.coords[:, 0], result.coords[:, 1], **params)
