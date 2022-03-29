from abc import ABC, abstractmethod
import argparse
from typing import Tuple, List

import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import cKDTree
import astropy.units as pq

from bob.snapshot import Snapshot
from bob.postprocessingFunctions import addToList, MultiSetFn
from bob.result import Result
from bob.simulationSet import SimulationSet
from bob.simulation import Simulation
from bob.basicField import BasicField
from bob.plots.slicePlot import findOrthogonalAxes
import bob.config as config
from bob.basicField import BasicField
from bob.allFields import allFields, getFieldByName

class TimePlot(MultiSetFn):
    @abstractmethod
    def getQuantity(self, sim: Simulation, snap: Snapshot) -> float:
        pass

    @abstractmethod
    def xlabel(self):
        pass
    
    @abstractmethod
    def ylabel(self):
        pass
    
    def post(self, args: argparse.Namespace, simSets: List[SimulationSet]) -> Result:
        self.field = getFieldByName(args.field)
        self.time = args.time
        return Result([self.getQuantityOverTime(args, simSet) for simSet in simSets])

    def plot(self, plt: plt.axes, result: Result) -> None:
        plt.xlabel(self.xlabel())
        plt.ylabel(self.ylabel())
        labels = ["100%", "200%", "TNG"]
        for (label, result) in zip(labels, result.arrs):
            print(result)
            plt.plot(result[:, 0], result[:, 1], label=label)
        plt.legend()

    def getQuantityOverTime(self, args: argparse.Namespace, simSet: SimulationSet) -> np.ndarray:
        snapshots = [(snap, sim) for sim in simSet for snap in sim.snapshots]
        snapshots.sort(key=lambda snapSim: snapSim[0].time)
        result = np.zeros((len(snapshots), 2))
        for (i, (snap, sim)) in enumerate(snapshots):
            result[i, 0] = self.getQuantity(args, sim, snap)
            if self.time == "z":
                result[i, 1] = sim.getRedshift(snap.scale_factor)
            elif self.time == "t":
                result[i, 1] = snap.time / pq.yr
        return result


class MeanFieldOverTime(TimePlot):
    def xlabel(self):
        return self.time

    def ylabel(self):
        return self.field.symbol

    def setArgs(self, subparser: argparse.ArgumentParser):
        subparser.add_argument("--field", required=True, choices=[f.niceName for f in allFields])
        subparser.add_argument("--time", default="t", choices=["t", "z"])

    def get_name(self, args: argparse.Namespace) -> str:
        return f"{self.name}_{args.field}_{args.time}"

    def getQuantity(self, args: argparse.Namespace, sim: Simulation, snap: Snapshot) -> float:
        data = self.field.getData(snap) / self.field.unit
        return np.mean(data)

addToList("meanFieldOverTime", MeanFieldOverTime())
