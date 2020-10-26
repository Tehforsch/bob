from typing import List, Any

from bob.simulationSet import SimulationSet
import matplotlib.pyplot as plt
from bob.postprocessingFunctions import addPlot

from bob.util import getNiceParamName


def getScalingSimSets(sims: SimulationSet, additionalParameters: List[str] = []) -> List[Any]:
    sims.sort(key=lambda sim: sim.params["numCores"])
    quotient = sims.quotient(["numCores"] + additionalParameters)
    quotient.sort(key=lambda sims: (sims[0]["SX_SWEEP"]))
    return quotient


@addPlot(None)
def speedup(ax: plt.axes, sims: SimulationSet) -> None:
    for (params, simSet) in getScalingSimSets(sims):
        numCores = [sim.params["numCores"] for sim in simSet]
        runTimes = [sim.runTime for sim in simSet]
        # ax.xscale("log")
        baseTime = runTimes[0]
        speedup = [0 if runTime is None else baseTime / runTime for runTime in runTimes]
        ax.xscale("log")
        ax.yscale("log")
        ax.xlabel("N")
        ax.ylabel("Speedup")
        ax.plot(numCores, speedup, label=",".join(getNiceParamName(k, v) for (k, v) in params.items()), marker="o")

    ax.plot(numCores, numCores, label="Ideal")
    ax.legend()


@addPlot(None)
def runTime(ax: plt.axes, sims: SimulationSet) -> None:
    for (params, simSet) in getScalingSimSets(sims):
        numCores = [sim.params["numCores"] for sim in simSet]
        runTimes = [sim.runTime for sim in simSet]
        ax.xlabel("N")
        ax.xscale("log")
        ax.yscale("log")
        ax.ylabel("run time [s]")
        ax.plot(numCores, runTimes, label=",".join(getNiceParamName(k, v) for (k, v) in params.items()), marker="o")
    # plt.plot(numCores, numCores, label="Ideal")
    ax.legend()


@addPlot(None)
def runTimeWeak(ax: plt.axes, sims: SimulationSet) -> None:
    for (params, simSet) in getScalingSimSets(sims, ["ReferenceGasPartMass"]):
        numCores = [sim.params["numCores"] for sim in simSet]
        runTimes = [sim.runTime for sim in simSet]
        ax.xlabel("N")
        ax.xscale("log")
        ax.yscale("log")
        ax.ylabel("run time [s]")
        ax.plot(numCores, runTimes, label=",".join(getNiceParamName(k, v) for (k, v) in params.items()), marker="o")
    # plt.plot(numCores, numCores, label="Ideal")
    ax.legend()


@addPlot(None)
def speedupWeak(ax: plt.axes, sims: SimulationSet) -> None:
    for (params, simSet) in getScalingSimSets(sims, ["ReferenceGasPartMass"]):
        numCores = [sim.params["numCores"] for sim in simSet]
        runTimes = [sim.runTime for sim in simSet]
        ax.xscale("log")
        baseTime = runTimes[0]
        speedup = [0 if runTime is None else baseTime / runTime for runTime in runTimes]
        ax.xlabel("N")
        ax.ylabel("Speedup")
        ax.plot(numCores, speedup, label=",".join(getNiceParamName(k, v) for (k, v) in params.items()), marker="o")

    ax.plot(numCores, [1 for core in numCores], label="Ideal")
    ax.legend()
