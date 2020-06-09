from bob.simulationSet import SimulationSet
import matplotlib.pyplot as plt


def scaling(sims: SimulationSet) -> None:
    for (params, simSet) in sims.quotient(["numCores"]):
        print(params, simSet)
        numCores = [sim.params["numCores"] for sim in simSet]
        runTimes = [sim.runTime for sim in simSet]
        plt.xscale("log")
        plt.plot(numCores, runTimes, label=str(params))
    plt.legend()
    plt.show()
