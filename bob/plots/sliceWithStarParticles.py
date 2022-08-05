import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

from bob.simulation import Simulation
from bob.snapshot import Snapshot
from bob.result import Result
from bob.plots.bobSlice import Slice
from bob.plotConfig import PlotConfig
from bob.plots.timePlots import getTimeOrRedshift


class SliceWithStarParticles(Slice):
    def __init__(self, config: PlotConfig) -> None:
        super().__init__(config)
        self.config.setDefault("circleSize", 0.05)

    def post(self, sim: Simulation, snap: Snapshot) -> Result:
        result = super().post(sim, snap)
        f = snap.hdf5File
        centerZ = snap.center[2]
        extentZ = (snap.maxExtent - snap.minExtent)[2]
        if "PartType4" in f:
            coords = snap.hdf5File["PartType4"]["Coordinates"] * snap.lengthUnit
            ids = snap.hdf5File["PartType4"]["ParticleIDs"][...]
            coords = coords[np.where(ids >= 0)]  # Filter out wind particles
            zRelativeDist = np.abs((coords[:, 2] - centerZ) / extentZ)
            result.coords = coords[np.where(zRelativeDist < 0.02)]
        else:
            result.coords = np.zeros(()) * snap.lengthUnit
        result.redshift = getTimeOrRedshift(sim, snap)
        return result

    def plot(self, plt: plt.axes, result: Result) -> None:
        if self.config["axis"] != "z":
            raise NotImplementedError("Implement other axes by adjusting the coordinates below")
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        super().plot(ax, result)
        if len(result.coords.shape) > 0:
            print(f"num stars: {result.coords.shape[0]}")
            for i in range(result.coords.shape[0]):
                coord = (result.coords[i, 0].to_value(self.config["xUnit"]), result.coords[i, 1].to_value(self.config["yUnit"]))
                circ = Circle((coord[0], coord[1]), self.config["circleSize"])
                ax.add_patch(circ)
