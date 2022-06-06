from typing import Dict, Any, List, Tuple
from abc import abstractmethod
import argparse

import matplotlib.pyplot as plt
import astropy.units as pq

import bob.config as config
from bob.snapshot import Snapshot
from bob.postprocessingFunctions import MultiSetFn
from bob.result import Result
from bob.simulationSet import SimulationSet
from bob.simulation import Simulation
from bob.multiSet import MultiSet
from bob.pool import runInPool
from bob.util import getArrayQuantity


def addTimeArg(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument("--time", default="t", choices=["t", "z"])


def getTimeQuantityForSnap(quantity: str, sim: Simulation, snap: Snapshot) -> float:
    return getTimeQuantityFromTimeOrScaleFactor(quantity, sim, snap, snap.scale_factor)


def getTimeQuantityFromTimeOrScaleFactor(quantity: str, sim: Simulation, snap: Snapshot, time_or_scale_factor: pq.Quantity) -> pq.Quantity:
    if quantity == "z":
        return sim.getRedshift(time_or_scale_factor)
    elif quantity == "t":
        if sim.params["ComovingIntegrationOn"]:
            return sim.getLookbackTime(time_or_scale_factor) / config.defaultTimeUnit
        else:
            return time_or_scale_factor * snap.timeUnit
    else:
        raise NotImplementedError


class TimePlot(MultiSetFn):
    def init(self, args: argparse.Namespace) -> None:
        super().init(args)
        self.styles: List[Dict[str, Any]] = [{} for _ in range(100)]

    @abstractmethod
    def getQuantity(self, args: argparse.Namespace, sim: Simulation, snap: Snapshot) -> pq.Quantity:
        pass

    def xlabel(self) -> str:
        return self.time

    @abstractmethod
    def ylabel(self) -> str:
        pass

    def post(self, args: argparse.Namespace, simSets: MultiSet) -> Result:
        self.labels = simSets.labels
        self.time = args.time
        results = Result()
        results.data = [self.getQuantityOverTime(args, simSet) for simSet in simSets]
        return results

    def plot(self, plt: plt.axes, result: Result) -> None:
        plt.xlabel(self.xlabel())
        plt.ylabel(self.ylabel())
        for (style, label, result) in zip(self.styles, self.labels, result.data):
            plt.plot(result.times, result.values, label=label)
        plt.legend()

    def getQuantityOverTime(self, args: argparse.Namespace, simSet: SimulationSet) -> Result:
        snapshots = [(snap, sim) for sim in simSet for snap in sim.snapshots]

        data = runInPool(getTimeAndResultForSnap, snapshots, self, args)
        data.sort(key=lambda x: x[0])
        result = Result()
        result.times = getArrayQuantity([x[0] for x in data])
        result.values = getArrayQuantity([x[1] for x in data])
        return result

    def setArgs(self, subparser: argparse.ArgumentParser) -> None:
        super().setArgs(subparser)
        addTimeArg(subparser)


def getTimeAndResultForSnap(plot: TimePlot, args: argparse.Namespace, snapSim: Tuple[Snapshot, Simulation]) -> Tuple[pq.Quantity, pq.Quantity]:
    (snap, sim) = snapSim
    return (getTimeQuantityForSnap(args.time, sim, snap), plot.getQuantity(args, sim, snap))
