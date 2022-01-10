from typing import List
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
def shadowing(ax: plt.axes, sim: Simulation) -> int:
    center = np.array([0.5, 0.5, 0.5])
    axis = np.array([1.0, 0.0, 0.0])
    abundance = BasicField("ChemicalAbundances", 1)
    density = BasicField("Density", None)
    criticalDensity = 1e9
    obstacle = TresholdField(density, criticalDensity, 0, 1)
    field = CombinedField([abundance, obstacle], [npRed, npBlue])

    snap = sim.snapshots[-1]
    voronoiSlice(ax, sim, snap, field, axis)
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


def bisectSnapTime(snaps: List[Snapshot], desiredTime: float):
    return snaps[bisectSnapTimeIndex(snaps, desiredTime, 0, len(snaps))]


def bisectSnapTimeIndex(
    snaps: List[Snapshot], desiredTime: float, minIndex: int, maxIndex: int
):
    middle = int((minIndex + maxIndex) / 2)
    print(minIndex, maxIndex, middle)
    if minIndex == middle or maxIndex == middle:
        return middle
    else:
        time = snaps[middle].time
        print(f"Checking {time} @ {middle}")
        if time < desiredTime:
            return bisectSnapTimeIndex(snaps, desiredTime, middle, maxIndex)
        else:
            return bisectSnapTimeIndex(snaps, desiredTime, minIndex, middle)


@addSingleSimPlot(None)
def shadowingDouble(ax: plt.axes, sim: Simulation) -> int:
    desiredTimes = [3200 * pq.year, 6500 * pq.year, 32000 * pq.year, 64000 * pq.year]
    snaps = [bisectSnapTime(sim.snapshots, desiredTime) for desiredTime in desiredTimes]
    print(snaps)
    for snap in snaps:
        axis = np.array([0.0, 0.0, 1.0])
        abundance = BasicField("ChemicalAbundances", 1)
        density = BasicField("Density", None)
        criticalDensity = 1e5
        obstacle = TresholdField(density, criticalDensity, 0, 1)
        field = CombinedField([abundance, obstacle], [npRed, npBlue])

        voronoiSlice(ax, sim, snap, field, axis)


# def findSnapshotsAtTimes(snapshots: List[Snapshot], times: List[float]) -> Iterator[Snapshot]:
#     unit = 1000 * pq.year
#     for time in times:
#         bestSnap = min(snapshots, key=lambda snap: abs(snap.time.rescale(unit) - time.rescale(unit)))
#         relativeError = (bestSnap.time - time) / time
#         if relativeError > 0.01:
#             print(f"ERR: Wanted snap at time {time} but the closest one is at {bestSnap.time}")
#         else:
#             print(f"Wanted snap at time {time}, found {bestSnap.time}")
#         yield bestSnap
