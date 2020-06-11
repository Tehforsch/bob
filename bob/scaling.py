from bob.simulationSet import SimulationSet
import matplotlib.pyplot as plt


def scaling(sims: SimulationSet) -> None:
    for (params, simSet) in sims.quotient(["numCores"]):
        print(params, simSet)
        numCores = [sim.params["numCores"] for sim in simSet]
        runTimes = [sim.runTime for sim in simSet]
        plt.xscale("log")
        baseTime = runTimes[0]
        print(runTimes)
        speedup = [baseTime / runTime for runTime in runTimes]
        plt.xlabel("N")
        plt.ylabel("Speedup")
        plt.plot(numCores, speedup, label=str(params))

    plt.plot(numCores, numCores, label="Ideal")
    plt.legend()
    plt.show()
