import argparse

import numpy as np
import matplotlib.pyplot as plt

from bob.result import Result
from bob.simulationSet import SimulationSet
from bob.postprocessingFunctions import SetFn
from bob.snapshot import Snapshot
from bob.field import Field
from bob.bobSlice import getDataAtPoints


class ShadowingLinePlot(SetFn):
    def post(self, args: argparse.Namespace, sims: SimulationSet) -> Result:
        snaps = [sim.snapshots[0] for sim in sims]
        print(snaps)
        return Result([])

    def getDataAlongLine(self, field: Field, snap: Snapshot, start: np.ndarray, end: np.ndarray) -> np.ndarray:
        numPoints = 100
        points = start + (end - start) * np.linspace(0.0, 1.0, numPoints)
        print(getDataAtPoints(field, snap, points))
        return np.zeros(1)

    def plot(self, plt: plt.axes, result: Result) -> None:
        print(result)
        raise ValueError
