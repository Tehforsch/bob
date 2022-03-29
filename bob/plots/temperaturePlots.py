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


class MeanFieldOverTime(MultiSetFn):
    def plot(self, plt: plt.axes, result: Result) -> None:
        plt.xlabel(self.xlabel())
        plt.ylabel(self.ylabel())
        labels = ["100%", "200%", "TNG"]
        for (label, result) in zip(labels, result.arrs):
            print(result)
            plt.plot(result[:, 0], result[:, 1], label=label)
        plt.legend()

    def xlabel(self):
        return self.time

    def ylabel(self):
        return self.field.symbol

    def post(self, args: argparse.Namespace, simSets: List[SimulationSet]) -> Result:
        self.field = getFieldByName(args.field)
        self.time = args.time
        return Result([self.getMeanFieldOverTime(simSet) for simSet in simSets])

    def getMeanFieldOverTime(self, simSet: SimulationSet) -> Result:
        snapshots = [(snap, sim) for sim in simSet for snap in sim.snapshots]
        snapshots.sort(key=lambda snapSim: snapSim[0].time)
        values = []
        times = []
        for (snap, sim) in snapshots:
            data = self.field.getData(snap)
            average = np.mean(data)
            print(snap, average)
            values.append(average / pq.K)
            if self.time == "z":
                times.append(sim.getRedshift(snap.scale_factor))
            elif self.time == "t":
                times.append(snap.time / pq.yr)

        return np.array([times, values]).transpose()

    def setArgs(self, subparser: argparse.ArgumentParser):
        subparser.add_argument("--field", required=True, choices=[f.niceName for f in allFields])
        subparser.add_argument("--time", default="t", choices=["t", "z"])

    def get_name(self, args: argparse.Namespace) -> str:
        return f"{self.name}_{args.field}_{args.time}"


addToList("meanFieldOverTime", MeanFieldOverTime())
