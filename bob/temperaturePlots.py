from typing import Tuple, List
import matplotlib.pyplot as plt
import numpy as np
from bob.snapshot import Snapshot
from bob.postprocessingFunctions import addMultiPlot
from bob.simulationSet import SimulationSet
from bob.simulation import Simulation
from bob.basicField import BasicField
from bob.temperature import Temperature
from bob.slicePlot import findOrthogonalAxes
import bob.config as config
from scipy.spatial import cKDTree


@addMultiPlot(None)
def temperatureOverRedshift(plt: plt.axes, simSets: List[SimulationSet]) -> None:
    plt.xlabel("z")
    plt.ylabel("T [K]")
    for (i, simSet) in enumerate(simSets):
        result = np.load(f"temperature{i}.npy")
        plt.plot(result[:, 0], result[:, 1])


def getTemperatureOverTime(simSet: SimulationSet) -> Tuple[List[float], List[float]]:
    snapshots = [(snap, sim) for sim in simSet for snap in sim.snapshots]
    snapshots.sort(key=lambda snapSim: -snapSim[0].time)
    temperatures = []
    redshifts = []
    for (snap, sim) in snapshots:
        temperature = Temperature().getData(snap)
        averageTemperature = np.mean(temperature)
        print(snap, averageTemperature)
        temperatures.append(averageTemperature)
        redshifts.append(sim.getRedshift(snap.scale_factor))
    return redshifts, temperatures