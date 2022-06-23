import argparse
import matplotlib.pyplot as plt

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
        for (redshift, volumeRate, massRate) in zip(result.redshift, result.volumeAvRate, result.massAvRate):
            self.addLine(redshift, volumeRate)
            self.addLine(redshift, massRate)


addToList("ionizationRate", IonizationRate())
