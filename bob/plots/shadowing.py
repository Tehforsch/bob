from typing import List, Dict, Any
import numpy as np
import matplotlib.pyplot as plt
import astropy.units as u
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

    snap = sim.snapshots[-1]
    voronoiSlice(ax, sim, snap, field, axis)
    assert sim.params["densityFunction"] in ["shadowing1", "shadowing2"]
    params: Dict[str, Any] = shadowing1Params if sim.params["densityFunction"] == "shadowing1" else shadowing2Params
    obstacleSize: float = params["size"]
    obstacleCenter: np.ndarray = params["center"]
    # ax.plot((center[2], center[1]), (obstacleCenter[2], obstacleCenter[1] - obstacleSize))
    x, y = center[2], center[1]
    ox, oy = obstacleCenter[2], obstacleCenter[1]
    delX = ox - x
    delY = oy - obstacleSize - y
    f = 2.0
    ax.plot((x, x + delX * f), (y, y + delY * f), color="green")
    ax.plot((x, x + delX * f), (y, y - delY * f), color="green")
    # ax.plot((center[1], center[2]), (obstacleCenter[2], obstacleCenter[1] + obstacleSize))


def bisectSnapTime(snaps: List[Snapshot], desiredTime: float) -> Snapshot:
    return snaps[bisectSnapTimeIndex(snaps, desiredTime, 0, len(snaps))]


def bisectSnapTimeIndex(snaps: List[Snapshot], desiredTime: float, minIndex: int, maxIndex: int) -> int:
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
def shadowingDouble(ax: plt.axes, sim: Simulation) -> None:
    desiredTimes = [3200 * u.year, 6500 * u.year, 32000 * u.year, 64000 * u.year]
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
