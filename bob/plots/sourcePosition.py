import argparse

import matplotlib.pyplot as plt

from bob.postprocessingFunctions import SetFn, addToList
from bob.result import Result
from bob.simulationSet import SimulationSet


class SourcePosition(SetFn):
    def post(self, args: argparse.Namespace, sims: SimulationSet) -> Result:
        result = Result()
        result.coords = [sim.sources().coord for sim in sims]
        return result

    def plot(self, axes: plt.axes, result: Result) -> None:
        for coords in result.coords:
            plt.scatter(coords[:, 0], coords[:, 1])


addToList("sourcePosition", SourcePosition())
