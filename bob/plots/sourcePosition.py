import argparse

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
        for (i, coords) in enumerate(result.coords):
            maxZ = np.max(coords[:, 2])
            xCoords = coords[np.where(coords[:, 2] < 0.1 * maxZ)][:, 0]
            yCoords = coords[np.where(coords[:, 2] < 0.1 * maxZ)][:, 1]
            plt.scatter(xCoords, yCoords)


addToList("sourcePosition", SourcePosition())
