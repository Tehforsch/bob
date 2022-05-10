from typing import Dict, Any, List
from abc import abstractmethod
import argparse

import matplotlib.pyplot as plt
import numpy as np

import bob.config as config
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
    def getQuantity(self, args: argparse.Namespace, sims: Simulation, snap: Snapshot) -> List[float]:
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
            plt.plot(arr[0, :], arr[1, :], label=label)
        plt.legend()

    def getQuantityOverTime(self, args: argparse.Namespace, simSet: SimulationSet) -> np.ndarray:
        snapshots = [(snap, sim) for sim in simSet for snap in sim.snapshots]
        snapshots.sort(key=lambda snapSim: snapSim[0].time)
        result = []
        for (i, (snap, sim)) in enumerate(snapshots):
            result.append([])
            result[-1].append(getTimeQuantityForSnap(args.time, sim, snap))
            for (j, value) in enumerate(self.getQuantity(args, sim, snap)):
                result[-1].append(value)
        return result

    def setArgs(self, subparser: argparse.ArgumentParser) -> None:
        super().setArgs(subparser)
        addTimeArg(subparser)


class MeanFieldOverTime(TimePlot):
    def init(self, args: argparse.Namespace) -> None:
        super().init(args)
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

    def getQuantity(self, args: argparse.Namespace, sim: Simulation, snap: Snapshot) -> List[float]:
        data = self.field.getData(snap) / self.field.unit
        return [np.mean(data)]

    def plot(self, plt: plt.axes, result: Result) -> None:
        if self.field.niceName == "Temperature":
            self.addConstraints(plt)
        super().plot(plt, result)

    def addConstraints(self, ax: plt.axes) -> None:
        boera19_temps = np.asarray([[4.6, 7.31e3, 0.88e3, 1.35e3], [5.0, 7.37e3, 1.39e3, 1.67e3]])

        walther19_zeds = np.asarray([4.6, 5.0, 5.4])
        walther19_temps = np.asarray([[0.877e4, 0.106e4, 0.130e4], [0.533e4, 0.091e4, 0.122e4], [0.599e4, 0.134e4, 0.152e4]])
        ax.errorbar(
            boera19_temps[:, 0],
            boera19_temps[:, 1],
            yerr=boera19_temps[:, 2:],
            label="Boera+19",
            c="k",
            ls="none",
            marker="D",
            capsize=3,
            elinewidth=1,
        )

        ax.errorbar(
            walther19_zeds - 0.01,
            walther19_temps[:, 0],
            yerr=walther19_temps[:, 1:].T,
            label="Walther+19",
            c="k",
            ls="none",
            marker="o",
            capsize=3,
            elinewidth=1,
        )


addToList("meanFieldOverTime", MeanFieldOverTime())
