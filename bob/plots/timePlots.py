from typing import Dict, Any, List, Tuple
from abc import abstractmethod
import argparse

import matplotlib.pyplot as plt
import numpy as np

import bob.config as config
from bob.snapshot import Snapshot
from bob.postprocessingFunctions import MultiSetFn
from bob.result import Result
from bob.simulationSet import SimulationSet
from bob.simulation import Simulation
from bob.multiSet import MultiSet
from bob.pool import runInPool


def addTimeArg(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument("--time", default="t", choices=["t", "z"])


def getTimeQuantityForSnap(quantity: str, sim: Simulation, snap: Snapshot) -> float:
    if quantity == "z":
        return sim.getRedshift(snap.scale_factor)
    elif quantity == "t":
        if sim.params["ComovingIntegrationOn"]:
            return sim.getLookbackTime(snap.scale_factor) / config.defaultTimeUnit
        else:
            return snap.time / config.defaultTimeUnit
    else:
        raise NotImplementedError


class TimePlot(MultiSetFn):
    def init(self, args: argparse.Namespace) -> None:
        super().init(args)
        self.styles: List[Dict[str, Any]] = [{} for _ in range(100)]

    @abstractmethod
    def getQuantity(self, args: argparse.Namespace, sim: Simulation, snap: Snapshot) -> List[float]:
        pass

    def xlabel(self) -> str:
        return self.time

    @abstractmethod
    def ylabel(self) -> str:
        pass

    def transform(self, result: np.ndarray) -> np.ndarray:
        return result

    def post(self, args: argparse.Namespace, simSets: MultiSet) -> Result:
        self.labels = simSets.labels
        self.time = args.time
        return Result([self.transform(self.getQuantityOverTime(args, simSet)) for simSet in simSets])

    def plot(self, plt: plt.axes, result: Result) -> None:
        plt.xlabel(self.xlabel())
        plt.ylabel(self.ylabel())
        for (style, label, arr) in zip(self.styles, self.labels, result.arrs):
            for i in range(1, arr.shape[1]):
                plt.plot(arr[:, 0], arr[:, i], label=label)
        plt.legend()

    def getQuantityOverTime(self, args: argparse.Namespace, simSet: SimulationSet) -> np.ndarray:
        snapshots = [(snap, sim) for sim in simSet for snap in sim.snapshots]

        result = runInPool(getTimeAndResultForSnap, snapshots, self, args)
        result.sort(key=lambda x: x[0])
        return np.array(result)

    def setArgs(self, subparser: argparse.ArgumentParser) -> None:
        super().setArgs(subparser)
        addTimeArg(subparser)


def getTimeAndResultForSnap(plot: TimePlot, args: argparse.Namespace, snapSim: Tuple[Snapshot, Simulation]) -> List[float]:
    (snap, sim) = snapSim
    result = []
    result.append(getTimeQuantityForSnap(args.time, sim, snap))
    for value in plot.getQuantity(args, sim, snap):
        result.append(value)
    return result
