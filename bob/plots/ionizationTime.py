import argparse
from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import cKDTree
import astropy.units as pq

from bob.simulationSet import SimulationSet
from bob.basicField import BasicField
from bob.plots.bobSlice import findOrthogonalAxes
import bob.config as config
from bob.result import Result
from bob.postprocessingFunctions import SetFn, addToList
from bob.plots.timePlots import addTimeArg, getTimeQuantityForSnap, getTimeQuantityFromTimeOrScaleFactor


class IonizationTime(SetFn):
    def post(self, args: argparse.Namespace, simSet: SimulationSet) -> Result:
        self.quantity = args.time
        ((self.min1, self.min2, self.max1, self.max2), data) = self.getIonizationTimeData(simSet)
        result = Result()
        result.data = data
        return result

    def plot(self, plt: plt.axes, result: Result) -> None:
        plt.xlabel("$x [h^{-1} \mathrm{Mpc}]$")
        plt.ylabel("$y [h^{-1} \mathrm{Mpc}]$")

        extent = (self.min1, self.max1, self.min2, self.max2)
        plt.imshow(result.data.to(pq.Myr), extent=extent, cmap="Reds", vmin=0, vmax=1000)
        cbar = plt.colorbar()
        cbar.set_label("$z$")

    def setArgs(self, subparser: argparse.ArgumentParser) -> None:
        super().setArgs(subparser)
        addTimeArg(subparser)

    def getIonizationTimeData(self, simSet: SimulationSet) -> Tuple[Tuple[float, float, float, float], np.ndarray]:
        axis = np.array([0.0, 0.0, 1.0])
        n1 = config.dpi * 3
        n2 = config.dpi * 3
        ionizationTime = None
        for sim in simSet:
            if len(sim.snapshots) == 0:
                print("No snapshots in sim? Continuing.")
                continue
            snap = max(sim.snapshots, key=lambda snap: getTimeQuantityForSnap(self.quantity, sim, snap))
            center = snap.center
            ortho1, ortho2 = findOrthogonalAxes(axis)
            min1 = np.dot(ortho1, snap.minExtent)
            min2 = np.dot(ortho2, snap.minExtent)
            max1 = np.dot(ortho1, snap.maxExtent)
            max2 = np.dot(ortho2, snap.maxExtent)
            p1, p2 = np.meshgrid(np.linspace(min1, max1, n1), np.linspace(min2, max2, n2))
            coordinates = axis * (center * axis) + np.outer(p1, ortho1) + np.outer(p2, ortho2)
            tree = cKDTree(snap.coordinates)
            cellIndices = tree.query(coordinates)[1]
            cellIndices = cellIndices.reshape((n1, n2))
            newIonizationTime = BasicField("IonizationTime").getData(snap)[cellIndices]
            newIonizationTime = getTimeQuantityFromTimeOrScaleFactor(self.quantity, sim, snap, newIonizationTime / snap.timeUnit)
            if ionizationTime is None:
                ionizationTime = newIonizationTime
            else:
                unit = ionizationTime.unit
                value1 = ionizationTime.to(unit).value
                value2 = newIonizationTime.to(unit).value
                ionizationTime = np.minimum(value1, value2) * unit
        if ionizationTime is not None:
            return (min1, min2, max1, max2), ionizationTime
        else:
            raise ValueError("No sims/snaps")


addToList("ionizationTime", IonizationTime())
