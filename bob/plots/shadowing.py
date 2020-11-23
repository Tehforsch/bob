from typing import Iterator, List
import numpy as np
import matplotlib.pyplot as plt
import quantities as pq
from bob.simulation import Simulation
from bob.combinedField import CombinedField
from bob.tresholdField import TresholdField
from bob.basicField import BasicField
from bob.slicePlot import voronoiSlice
from bob.postprocessingFunctions import addSingleSimPlot
from bob.icsDefaults import shadowing1Params, shadowing2Params
from bob.snapshot import Snapshot

from bob.config import npRed, npBlue


@addSingleSimPlot(None)
def shadowing(ax: plt.axes, sim: Simulation) -> None:
    center = np.array([0.5, 0.5, 0.5])
    axis = np.array([1.0, 0.0, 0.0])
    abundance = BasicField("ChemicalAbundances", 1)
    density = BasicField("Density", None)
    criticalDensity = 1e9
    obstacle = TresholdField(density, criticalDensity, 0, 1)
    field = CombinedField([abundance, obstacle], [npRed, npBlue])

    kiloyear = pq.year * pq.kilo
    snapshots = findSnapshotsAtTimes(sim.snapshots, [3.2 * kiloyear, 6.5 * kiloyear, 32 * kiloyear, 64 * kiloyear])
    for snap in snapshots:
        voronoiSlice(ax, sim.snapshots, field, center, axis)
        if sim.params["densityFunction"] == "shadowingCenter":
            return
        assert sim.params["densityFunction"] in ["shadowing1", "shadowing2"]
        if sim.params["densityFunction"] == "shadowing1":
            params = shadowing1Params
        else:
            params = shadowing2Params
        obstacleSize = params["size"]
        obstacleCenter = params["center"]
        # ax.plot((center[2], center[1]), (obstacleCenter[2], obstacleCenter[1] - obstacleSize))
        x, y = center[2], center[1]
        ox, oy = obstacleCenter[2], obstacleCenter[1]
        delX = ox - x
        delY = oy - obstacleSize - y
        f = 2.0
        ax.plot((x, x + delX * f), (y, y + delY * f), color="green")
        ax.plot((x, x + delX * f), (y, y - delY * f), color="green")
        # ax.plot((center[1], center[2]), (obstacleCenter[2], obstacleCenter[1] + obstacleSize))


def findSnapshotsAtTimes(snapshots: List[Snapshot], times: List[float]) -> Iterator[Snapshot]:
    for time in times:
        bestSnap = max(snapshots, key=lambda snap: abs(snap.time - time))
        relativeError = (bestSnap.time - time) / time
        if relativeError > 0.01:
            print("Wanted snap at time {} but the closest one is at {}", time, bestSnap.time)
        yield bestSnap
