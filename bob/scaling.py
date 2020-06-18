from typing import List, Any

from bob.simulationSet import SimulationSet
import matplotlib.pyplot as plt


def getScalingSimSets(sims: SimulationSet) -> List[Any]:
    sims.sort(key=lambda sim: sim.params["numCores"])
    quotient = sims.quotient(["numCores"])
    quotient.sort(key=lambda sims: (sims[0]["SX_SWEEP"], sims[0]["MultipleDomains"]))
    return quotient


def speedup(ax: plt.axes, sims: SimulationSet) -> None:
    for (params, simSet) in getScalingSimSets(sims):
        numCores = [sim.params["numCores"] for sim in simSet]
        runTimes = [sim.runTime for sim in simSet]
        # ax.xscale("log")
        baseTime = runTimes[0]
        speedup = [None if runTime is None else baseTime / runTime for runTime in runTimes]
        ax.xlabel("N")
        ax.ylabel("Speedup")
        ax.plot(numCores, speedup, label=str(params))

    ax.plot(numCores, numCores, label="Ideal")
    ax.legend()


def runTime(ax: plt.axes, sims: SimulationSet) -> None:
    for (params, simSet) in getScalingSimSets(sims):
        numCores = [sim.params["numCores"] for sim in simSet]
        runTimes = [sim.runTime for sim in simSet]
        ax.xlabel("N")
        ax.ylabel("run time [s]")
        ax.plot(numCores, runTimes, label=str(params))

    # plt.plot(numCores, numCores, label="Ideal")
    ax.legend()
