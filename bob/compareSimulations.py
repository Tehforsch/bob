import itertools
import logging
import numpy as np
import matplotlib.pyplot as plt
from typing import Callable, Any, List

from bob.field import Field
from bob.simulationSet import SimulationSet
from bob.snapshot import Snapshot
from bob.simulation import Simulation
from bob.util import getNiceTimeUnitName


# def fieldDifference(ax: plt.axes, sim1: Simulation, sim2: Simulation, field: Field) -> None:
#     data = []
#     times = []
#     for (snap1, snap2) in zip(sim1.snapshots, sim2.snapshots):
#         assert snap1.time == snap2.time
#         f1 = field.getData(snap1)
#         f2 = field.getData(snap2)
#         assert f1.shape == f2.shape
#         diff = np.abs(getRelativeDifference(f1, f2))
#         maxDiff = np.max(diff)
#         minDiff = np.min(diff)
#         averageDiff = np.mean(diff)
#         times.append(snap1.time)
#         data.append(averageDiff)
#         numCells = np.where(diff > 0.5)
#         logging.info(f"Relative difference for chemical abundance 1: Max: {maxDiff}, Min: {minDiff}, Average: {averageDiff}")
#         logging.info("#Cells with difference > 0.5: {}".format(len(numCells[0])))
#     ax.plot(times, data)
#     niceTimeUnitName = getNiceTimeUnitName(sim1.snapshots[0].t_unit)
#     ax.xlabel(f"Time [{niceTimeUnitName}]")
#     ax.ylabel(f"Relative error {field.niceName}")


# def plotFieldDifference(ax: plt.axes, sim1: Simulation, sim2: Simulation, field: Field) -> None:
#     snap1 = sim1.snapshots[-1]
#     snap2 = sim2.snapshots[-1]
#     f1 = field.getData(snap1)
#     f2 = field.getData(snap2)
#     print(f1.shape, f2.shape)
#     return
#     # assert f1.shape == f2.shape, f"Shapes differ: {f1.shape}, {f2.shape}"
#     ax3d = get3DAx(ax)
#     diff = getAbsoluteDifference(f1, f2)
#     where = np.where(np.abs(diff) >= 0.5)
#     coords = [snap1.coordinates[where, i] for i in range(3)]
#     ax3d.scatter(*coords, c=diff[where])


# # The actual functions we can call. Rewrite to automatically generate these if it becomes too much
# def compareAbundance(ax: plt.axes, sims: SimulationSet) -> None:
#     compare(ax, sims, Field("ChemicalAbundances", 1))


# def comparePhotonFlux(ax: plt.axes, sims: SimulationSet) -> None:
#     compare(ax, sims, Field("PhotonFlux", 2))


# def plotAbundanceDifference(ax: plt.axes, sims: SimulationSet) -> None:
#     plotDifference(ax, sims, Field("ChemicalAbundances", 1))


# def plotPhotonFluxDifference(ax: plt.axes, sims: SimulationSet) -> None:
#     plotDifference(ax, sims, Field("PhotonFlux", 2))


def compare(ax: plt.axes, sims: SimulationSet, field: Field) -> None:
    diff = lambda sim1, sim2: fieldDifference(ax, sim1, sim2, field)
    compareSimSet(sims, diff)


def plotDifference(ax: plt.axes, sims: SimulationSet, field: Field) -> None:
    plotDiff = lambda sim1, sim2: plotFieldDifference(ax, sim1, sim2, field)
    compareSimSet(sims, plotDiff)


def compareSimSet(sims: SimulationSet, compareFunction: Callable[..., Any]) -> None:
    for (sim1, sim2) in itertools.combinations(sims, r=2):
        logging.info(f"Comparing {sim1} {sim2}. Parameters:")
        for param in sims.variedParams:
            logging.info("{}: {} {}".format(param, sim1.params[param], sim2.params[param]))
        compareFunction(sim1, sim2)


postprocessFunctions: List[Callable[[SimulationSet], None]] = []
plotFunctions: List[Callable[[plt.axes, SimulationSet], None]] = []
