from typing import Tuple
from abc import abstractmethod

import matplotlib.pyplot as plt
import astropy.units as pq

from bob.snapshot import Snapshot
from bob.postprocessingFunctions import MultiSetFn, PostprocessingFunction
from bob.result import Result
from bob.simulationSet import SimulationSet
from bob.simulation import Simulation
from bob.multiSet import MultiSet
from bob.pool import runInPool
from bob.util import getArrayQuantity


def addTimeArg(fn: PostprocessingFunction) -> None:
    fn.config.setDefault("time", "t", choices=["t", "z"])


def getTimeQuantityForSnap(quantity: str, sim: Simulation, snap: Snapshot) -> float:
    return getTimeQuantityFromTimeOrScaleFactor(quantity, sim, snap, snap.scale_factor)


def getTimeQuantityFromTimeOrScaleFactor(quantity: str, sim: Simulation, snap: Snapshot, time_or_scale_factor: pq.Quantity) -> pq.Quantity:
    if quantity == "z":
        return sim.getRedshift(time_or_scale_factor) * pq.dimensionless_unscaled
    elif quantity == "t":
        if sim.params["ComovingIntegrationOn"]:
            return sim.getLookbackTime(time_or_scale_factor)
        else:
            return time_or_scale_factor * snap.timeUnit
    else:
        raise NotImplementedError


def getTimeOrRedshift(sim: Simulation, snap: Snapshot) -> pq.Quantity:
    if sim.params["ComovingIntegrationOn"] == 1:
        return getTimeQuantityForSnap("z", sim, snap)
    else:
        return getTimeQuantityForSnap("t", sim, snap)


class TimePlot(MultiSetFn):
    def __init__(self) -> None:
        super().__init__()
        addTimeArg(self)

    @abstractmethod
    def getQuantity(self, sim: Simulation, snap: Snapshot) -> pq.Quantity:
        pass

    def xlabel(self) -> str:
        return self.config["time"]

    @abstractmethod
    def ylabel(self) -> str:
        pass

    def post(self, simSets: MultiSet) -> Result:
        results = Result()
        results.data = [self.getQuantityOverTime(self.config["time"], simSet) for simSet in simSets]
        return results

    def plot(self, plt: plt.axes, result: Result) -> None:
        self.config.setDefault("xUnit", "Myr")
        self.config.setDefault("xLabel", format(f"{self.xlabel()} [UNIT]"))
        self.config.setDefault("yLabel", format(f"{self.ylabel()} [UNIT]"))
        self.setupLinePlot()
        for (label, result) in zip(self.getLabels(), result.data):
            self.addLine(result.times, result.values, label=label)
        plt.legend()

    def getQuantityOverTime(self, timeQuantity: str, simSet: SimulationSet) -> Result:
        snapshots = [(snap, sim) for sim in simSet for snap in sim.snapshots]

        data = runInPool(getTimeAndResultForSnap, snapshots, self, timeQuantity)
        data.sort(key=lambda x: x[0])
        result = Result()
        result.times = getArrayQuantity([x[0] for x in data])
        result.values = getArrayQuantity([x[1] for x in data])
        return result


def getTimeAndResultForSnap(plot: TimePlot, timeQuantity: str, snapSim: Tuple[Snapshot, Simulation]) -> Tuple[pq.Quantity, pq.Quantity]:
    (snap, sim) = snapSim
    return (getTimeQuantityForSnap(timeQuantity, sim, snap), plot.getQuantity(sim, snap))
