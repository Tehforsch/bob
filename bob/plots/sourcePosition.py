import argparse

import astropy.units as pq
import matplotlib.pyplot as plt
import numpy as np

from bob.postprocessingFunctions import SetFn, addToList
from bob.result import Result
from bob.simulationSet import SimulationSet


class SourcePosition(SetFn):
    def post(self, args: argparse.Namespace, sims: SimulationSet) -> Result:
        result = Result()
        result.coords = [sim.sources().coord * sim.snapshots[0].lengthUnit for sim in sims]
        return result

    def plot(self, axes: plt.axes, result: Result) -> None:
        self.style.setDefault("xLim", (np.min(result.coords[-1][:, 0]), np.max(result.coords[-1][:, 0])))
        self.style.setDefault("yLim", (np.min(result.coords[-1][:, 1]), np.max(result.coords[-1][:, 1])))
        self.style.setDefault("xUnit", pq.kpc)
        self.style.setDefault("yUnit", pq.kpc)
        self.style.setDefault("xLabel", "x [UNIT]")
        self.style.setDefault("yLabel", "y [UNIT]")
        for (i, coords) in enumerate(result.coords):
            maxZ = np.max(coords[:, 2])
            xCoords = coords[np.where(coords[:, 2] < 0.1 * maxZ)][:, 0]
            yCoords = coords[np.where(coords[:, 2] < 0.1 * maxZ)][:, 1]
            self.scatter(xCoords, yCoords)


addToList("sourcePosition", SourcePosition())
