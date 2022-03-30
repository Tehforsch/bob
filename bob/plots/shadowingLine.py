import argparse

import matplotlib.pyplot as plt

from bob.result import Result
from bob.simulationSet import SimulationSet
from bob.postprocessingFunctions import SetFn


class ShadowingLinePlot(SetFn):
    def post(self, args: argparse.Namespace, sims: SimulationSet) -> Result:
        snaps = [sim.snapshots[0] for sim in sims]
        print(snaps)
        return Result([])

    def plot(self, plt: plt.axes, result: Result) -> None:
        print(result)
        raise ValueError
