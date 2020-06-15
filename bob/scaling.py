from typing import List, Any

from bob.simulationSet import SimulationSet
import matplotlib.pyplot as plt


def getScalingSimSets(sims: SimulationSet) -> List[Any]:
    sims.sort(key=lambda sim: sim.params["numCores"])
    return sims.quotient(["numCores"])


def speedup(sims: SimulationSet) -> None:
    for (params, simSet) in getScalingSimSets(sims):
        numCores = [sim.params["numCores"] for sim in simSet]
        runTimes = [sim.runTime for sim in simSet]
        # plt.xscale("log")
        baseTime = runTimes[0]
        speedup = [None if runTime is None else baseTime / runTime for runTime in runTimes]
        plt.xlabel("N")
        plt.ylabel("Speedup")
        plt.plot(numCores, speedup, label=str(params))

    # plt.plot(numCores, numCores, label="Ideal")
    plt.legend()
    plt.show()


def runTime(sims: SimulationSet) -> None:
    for (params, simSet) in getScalingSimSets(sims):
        numCores = [sim.params["numCores"] for sim in simSet]
        runTimes = [sim.runTime for sim in simSet]
        plt.xlabel("N")
        plt.ylabel("run time [s]")
        plt.plot(numCores, runTimes, label=str(params))

    # plt.plot(numCores, numCores, label="Ideal")
    plt.legend()
    plt.show()
