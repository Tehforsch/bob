import argparse

import numpy as np
import matplotlib.pyplot as plt
import astropy.units as pq

from bob.result import Result
from bob.simulationSet import SimulationSet
from bob.postprocessingFunctions import SetFn, addToList
from bob.snapshot import Snapshot
from bob.field import Field
from bob.plots.bobSlice import getDataAtPoints
from bob.basicField import BasicField


class ShadowingLinePlot(SetFn):
    def post(self, args: argparse.Namespace, sims: SimulationSet) -> Result:
        snaps = [sim.snapshots[-1] for sim in sims]
        print("Using snaps at times:", ",".join(str(snap.time.to(pq.Myr)) for snap in snaps))
        start = np.array([0.5, 0.5, 0.5])
        end = np.array([1.0, 1.0, 0.5])
        data = [self.getDataAlongLine(BasicField("ChemicalAbundances", 1), snap, start, end) for snap in snaps]
        return Result(data)

    def getDataAlongLine(self, field: Field, snap: Snapshot, start: np.ndarray, end: np.ndarray) -> np.ndarray:
        numPoints = 100
        result = np.zeros((2, numPoints))
        fractions = np.linspace(0.0, 1.0, numPoints)
        offsets = np.outer(end - start, fractions).transpose()
        points = np.add(start, offsets)
        result[1, :] = getDataAtPoints(field, snap, points)
        result[0, :] = fractions
        return result

    def plot(self, plt: plt.axes, result: Result) -> None:
        for arr in result.arrs:
            plt.plot(arr[0, :], arr[1, :])


addToList("shadowingLine", ShadowingLinePlot())
