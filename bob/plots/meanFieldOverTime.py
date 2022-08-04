import argparse

import matplotlib.pyplot as plt
import numpy as np

from bob.field import Field
from bob.snapshot import Snapshot
from bob.postprocessingFunctions import addToList
from bob.result import Result
from bob.simulation import Simulation
from bob.allFields import allFields, getFieldByName
from bob.basicField import BasicField
from bob.plots.timePlots import TimePlot


class MeanFieldOverTime(TimePlot):
    def xlabel(self) -> str:
        return self.config["time"]

    def ylabel(self) -> str:
        return self.field().symbol

    def field(self) -> Field:
        return getFieldByName(self.config["field"])

    def setArgs(self) -> None:
        super().setArgs()
        self.config.setRequired("field", choices=[f.niceName for f in allFields])

    def getName(self, args: argparse.Namespace) -> str:
        field = self.config["field"]
        timeQuantity = self.config["time"]
        return f"{self.name}_{field}_{timeQuantity}"

    def getQuantity(self, sim: Simulation, snap: Snapshot) -> float:
        masses = BasicField("Masses").getData(snap)
        data = self.field().getData(snap)
        return np.mean(data * masses) / np.mean(masses)

    def plot(self, plt: plt.axes, result: Result) -> None:
        self.config.setDefault("yUnit", self.field().unit)
        super().plot(plt, result)


addToList("meanFieldOverTime", MeanFieldOverTime())
