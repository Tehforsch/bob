import argparse
import matplotlib.pyplot as plt
import astropy.units as pq
import itertools

from bob.postprocessingFunctions import MultiSetFn, addToList
from bob.result import Result
from bob.multiSet import MultiSet
from bob.plots.ionization import IonizationData


class IonizationRate(MultiSetFn):
    def post(self, args: argparse.Namespace, simSets: MultiSet) -> Result:
        self.labels = simSets.labels
        result = IonizationData(simSets)
        return result

    def plot(self, plt: plt.axes, result: Result) -> None:
        self.style.setDefault("xLabel", "z")
        self.style.setDefault("yLabel", "R")
        self.style.setDefault("xUnit", pq.dimensionless_unscaled)
        self.style.setDefault("yUnit", 1 / pq.s)
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.set_yscale("log")
        self.setupLinePlot()
        colors = ["b", "r", "g", "purple", "brown", "orange"]
        for (redshift, volumeRate, massRate, color) in zip(result.redshift, result.volumeAvRate, result.massAvRate, itertools.cycle(colors)):
            self.addLine(redshift, volumeRate, color=color, linestyle="-")
            self.addLine(redshift, massRate, color=color, linestyle="--")


addToList("ionizationRate", IonizationRate())
