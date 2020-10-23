import numpy as np
import matplotlib.pyplot as plt
from bob.simulation import Simulation
from bob.combinedField import CombinedField
from bob.tresholdField import TresholdField
from bob.basicField import BasicField
from bob.slicePlot import voronoiSlice
from bob.postprocessingFunctions import addSingleSimPlot
from bob.icsDefaults import shadowing1Params, shadowing2Params

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

    voronoiSlice(ax, sim.snapshots[-1], field, center, axis)
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
