from abc import abstractmethod
import argparse

import matplotlib.pyplot as plt
import numpy as np
import astropy.units as pq

from bob.snapshot import Snapshot
from bob.postprocessingFunctions import addToList, MultiSetFn
from bob.result import Result
from bob.simulationSet import SimulationSet
from bob.simulation import Simulation
from bob.allFields import allFields, getFieldByName
from bob.multiSet import MultiSet


def addTimeArg(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument("--time", default="t", choices=["t", "z"])


def getTimeQuantityForSnap(quantity: str, sim: Simulation, snap: Snapshot) -> float:
    if quantity == "z":
        return sim.getRedshift(snap.scale_factor)
    elif quantity == "t":
        if sim.params["ComovingIntegrationOn"]:
            return sim.getLookbackTime(snap.scale_factor) / pq.yr
        else:
            return snap.time / pq.yr
    else:
        raise NotImplementedError


class TimePlot(MultiSetFn):
    def init(self, args: argparse.Namespace) -> None:
        pass

    @abstractmethod
    def getQuantity(self, args: argparse.Namespace, sims: Simulation, snap: Snapshot) -> float:
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
        self.init(args)
        self.time = args.time
        return Result([self.transform(self.getQuantityOverTime(args, simSet)) for simSet in simSets])

    def plot(self, plt: plt.axes, result: Result) -> None:
        plt.xlabel(self.xlabel())
        plt.ylabel(self.ylabel())
        for (label, arr) in zip(self.labels, result.arrs):
            plt.plot(arr[0, :], arr[1, :], label=label)
        plt.legend()

    def getQuantityOverTime(self, args: argparse.Namespace, simSet: SimulationSet) -> np.ndarray:
        snapshots = [(snap, sim) for sim in simSet for snap in sim.snapshots]
        snapshots.sort(key=lambda snapSim: snapSim[0].time)
        result = np.zeros((2, len(snapshots)))
        for (i, (snap, sim)) in enumerate(snapshots):
            result[0, i] = getTimeQuantityForSnap(args.time, sim, snap)
            result[1, i] = self.getQuantity(args, sim, snap)
        return result

    def setArgs(self, subparser: argparse.ArgumentParser) -> None:
        super().setArgs(subparser)
        addTimeArg(subparser)


class MeanFieldOverTime(TimePlot):
    def init(self, args: argparse.Namespace) -> None:
        self.field = getFieldByName(args.field)

    def xlabel(self) -> str:
        return self.time

    def ylabel(self) -> str:
        return self.field.symbol

    def setArgs(self, subparser: argparse.ArgumentParser) -> None:
        super().setArgs(subparser)
        subparser.add_argument("--field", required=True, choices=[f.niceName for f in allFields])

    def getName(self, args: argparse.Namespace) -> str:
        return f"{self.name}_{args.field}_{args.time}"

    def getQuantity(self, args: argparse.Namespace, sim: Simulation, snap: Snapshot) -> float:
        data = self.field.getData(snap) / self.field.unit
        return np.mean(data)


addToList("meanFieldOverTime", MeanFieldOverTime())
