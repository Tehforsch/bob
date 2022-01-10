from typing import List, Any, Dict

from bob.simulationSet import SimulationSet
import matplotlib.pyplot as plt
from bob.postprocessingFunctions import addPlot

from bob.util import getNiceParamName


class ScalingSet:
    def __init__(self, params: Dict[str, Any], sim_set: SimulationSet) -> None:
        self.simSet = sim_set
        self.params = params
        self.numCores = [sim.params["numCores"] for sim in self.simSet]
        self.runTimes = [sim.runTime for sim in self.simSet]
        self.baseNumCores = self.numCores[0]
        self.baseRunTime = self.runTimes[0]
        self.speedup = [0 if runTime is None else self.baseRunTime / runTime for runTime in self.runTimes]
        self.idealSpeedup = [n / self.baseNumCores for n in self.numCores]
        self.efficiency = [speedup / idealSpeedup for (speedup, idealSpeedup) in zip(self.speedup, self.idealSpeedup)]


def comparable(k: str, v: Any) -> Any:
    if k == "InitCondFile":
        return float(v.replace("ics_", ""))
    else:
        return v


def getScalingSimSets(sims: SimulationSet, additionalParameters: List[str] = []) -> List[Any]:
    quotient = sims.quotient(additionalParameters)
    quotient.sort(key=lambda sims: tuple(comparable(param, sims[1][0].params[param]) for param in additionalParameters))
    return [ScalingSet(params, simSet) for (params, simSet) in quotient]


@addPlot(None)
def speedupResolutions(ax: plt.axes, sims: SimulationSet) -> None:
    sets = getScalingSimSets(sims, ["InitCondFile"])
    for scaling in sets:
        ax.xscale("log")
        ax.xlabel("N")
        ax.ylabel("Speedup")
        ax.plot(
            scaling.numCores,
            scaling.speedup,
            label=",".join(getNiceParamName(k, v) for (k, v) in scaling.params.items()),
            marker="o",
        )
    plt.gca().set_prop_cycle(None)
    for scaling in sets:
        ax.plot(scaling.numCores, scaling.idealSpeedup)

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
        ax.plot(
            numCores,
            runTimes,
            label=",".join(getNiceParamName(k, v) for (k, v) in params.items()),
            marker="o",
        )
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
        ax.plot(
            numCores,
            runTimes,
            label=",".join(getNiceParamName(k, v) for (k, v) in params.items()),
            marker="o",
        )
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
        ax.plot(
            numCores,
            speedup,
            label=",".join(getNiceParamName(k, v) for (k, v) in params.items()),
            marker="o",
        )

    ax.plot(numCores, [1 for core in numCores], label="Ideal")
    ax.legend()
