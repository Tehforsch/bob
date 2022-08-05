import astropy.units as pq
import matplotlib.pyplot as plt
import numpy as np

from bob.postprocessingFunctions import SetFn
from bob.result import Result
from bob.simulationSet import SimulationSet
from bob.plotConfig import PlotConfig


class SourcePosition(SetFn):
    def __init__(self, config: PlotConfig) -> None:
        super().__init__(config)
        self.config.setDefault("xLim", (0.0, 1.0))
        self.config.setDefault("yLim", (0.0, 1.0))
        self.config.setDefault("xUnit", pq.kpc)
        self.config.setDefault("yUnit", pq.kpc)
        self.config.setDefault("xLabel", "x [UNIT]")
        self.config.setDefault("yLabel", "y [UNIT]")

    def post(self, sims: SimulationSet) -> Result:
        result = Result()
        result.coords = [sim.sources().coord * sim.snapshots[0].lengthUnit for sim in sims]
        self.config.setDefault("xLim", (np.min(result.coords[-1][:, 0]), np.max(result.coords[-1][:, 0])))
        self.config.setDefault("yLim", (np.min(result.coords[-1][:, 1]), np.max(result.coords[-1][:, 1])))
        return result

    def plot(self, axes: plt.axes, result: Result) -> None:
        for (i, coords) in enumerate(result.coords):
            maxZ = np.max(coords[:, 2])
            xCoords = coords[np.where(coords[:, 2] < 0.1 * maxZ)][:, 0]
            yCoords = coords[np.where(coords[:, 2] < 0.1 * maxZ)][:, 1]
            self.scatter(xCoords, yCoords)
