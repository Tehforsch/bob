import argparse
import matplotlib.pyplot as plt
import astropy.units as pq

from bob.postprocessingFunctions import MultiSetFn, addToList
from bob.result import Result
from bob.multiSet import MultiSet
from bob.plots.ionization import IonizationData


class IonizationRate(MultiSetFn):
    def post(self, args: argparse.Namespace, simSets: MultiSet) -> Result:
        result = IonizationData(simSets)
        return result

    def plot(self, plt: plt.axes, result: Result) -> None:
        self.style.setDefault("xLabel", "z")
        self.style.setDefault("yLabel", "R")
        self.style.setDefault("xUnit", pq.dimensionless_unscaled)
        self.style.setDefault("yUnit", 1 / pq.s)
        self.style.setDefault("legend_loc", "lower left")
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.set_yscale("log")
        self.setupLinePlot()
        labels = self.getLabels()
        colors = self.getColors()
        for (redshift, volumeRate, massRate, color, label) in zip(result.redshift, result.volumeAvRate, result.massAvRate, colors, labels):
            self.addLine(redshift, volumeRate, color=color, linestyle="-", label=label)
            self.addLine(redshift, massRate, color=color, linestyle="--", label="")
        plt.plot([], [], color="black", linestyle="-", label="volume av.")
        plt.plot([], [], color="black", linestyle="--", label="mass av.")
        plt.legend(loc=self.style["legend_loc"])


addToList("ionizationRate", IonizationRate())
