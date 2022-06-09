import argparse

import matplotlib.pyplot as plt
import numpy as np

from bob.snapshot import Snapshot
from bob.postprocessingFunctions import addToList
from bob.result import Result
from bob.simulation import Simulation
from bob.allFields import allFields, getFieldByName
from bob.basicField import BasicField
from bob.plots.timePlots import TimePlot


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

    def getQuantity(self, args: argparse.Namespace, sim: Simulation, snap: Snapshot) -> float:
        masses = BasicField("Masses").getData(snap)
        data = self.field.getData(snap)
        return np.mean(data * masses) / np.mean(masses)

    def plot(self, plt: plt.axes, result: Result) -> None:
        self.style.setDefault("yUnit", self.field.unit)
        super().plot(plt, result)


addToList("meanFieldOverTime", MeanFieldOverTime())
