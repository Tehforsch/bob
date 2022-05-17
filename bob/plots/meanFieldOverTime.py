import argparse

import matplotlib.pyplot as plt
import numpy as np
from typing import List

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

    def getQuantity(self, args: argparse.Namespace, sim: Simulation, snap: Snapshot) -> List[float]:
        masses = BasicField("Masses").getData(snap)
        data = self.field.getData(snap) / self.field.unit
        return [np.mean(data * masses) / np.mean(masses)]

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
