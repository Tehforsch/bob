from typing import Any, Tuple
import numpy as np
import matplotlib.pyplot as plt
import astropy.units as pq
from astropy.io import ascii

import itertools
from bob.postprocessingFunctions import MultiSetFn
from bob.result import Result
from bob.multiSet import MultiSet
from bob.plots.ionization import IonizationData
from bob.plotConfig import PlotConfig
from bob.util import getDataFile


class IonizationRate(MultiSetFn):
    def __init__(self, config: PlotConfig) -> None:
        super().__init__(config)
        self.config.setDefault("xLabel", "z")
        self.config.setDefault("yLabel", "R")
        self.config.setDefault("xUnit", pq.dimensionless_unscaled)
        self.config.setDefault("yUnit", 1 / pq.s)
        self.config.setDefault("legend_loc", "upper right")
        self.config.setDefault("yLim", [1e-18, 1e-12])
        self.config.setDefault("xLim", [20, 0])

    def post(self, simSets: MultiSet) -> Result:
        for label, sims in zip(self.getLabels(), simSets):
            print(label, sims[0].folder)
        data = [IonizationData(sim, skip=5) for sim in simSets]
        result = Result()
        result.data = data
        return result

    def plot(self, plt: plt.axes, result: Result) -> None:
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.set_yscale("log")
        self.setupLinePlot()
        labels = self.getLabels()
        colors = self.getColors()
        for data, color, label in zip(result.data, itertools.cycle(colors), self.getLabels()):
            for redshift, volumeRate in zip(data.redshift, data.volumeAvRate):
                self.addLine(redshift, volumeRate, color=color, linestyle="-", label=label)
        # plt.plot([], [], color="black", linestyle="-", label="volume av.")
        self.addConstraints()
        plt.legend(loc=self.config["legend_loc"])

    def addConstraints(self) -> None:
        data = readAscii("faucher-giguere2008/table1")
        [zfc08, tauafc08, taubfc08, gamfc08, e_gamfc08] = data.T

        data = readAscii("becker_bolton2013/table1")
        [zbb13, lgambb13, erplgbb13, ermlgbb13] = data
        (gambb13, erpgbb13, ermgbb13) = logToLin(lgambb13, ermlgbb13, erplgbb13)

        data = readAscii("daloisio2018/table2")
        [zdal18, gamdal18, erpdal18, ermdal18] = data

        zcal11 = [5.0, 6.0]
        lgammacal11 = np.array([-12.15, -12.84])  # loggamma calverley 2011
        erlgammacal11 = np.array([0.16, 0.18])  # log error
        gammacal11, ermgammacal11, erpgammacal11 = logToLin(lgammacal11, erlgammacal11, erlgammacal11)

        plt.errorbar(zcal11, gammacal11, yerr=[ermgammacal11, erpgammacal11], fmt="o", color="r", mec="r", label=r"Calverley+11", capsize=5)
        # plt.errorbar(zfc08, gamfc08 * 1e-12, yerr=e_gamfc08 * 1e-12, fmt="s", color="g", mec="g", label=r"Faucher-Giguere+08", capsize=5)
        # plt.errorbar(
        #     zbb13, gambb13 * 1e-12, yerr=[-erpgbb13 * 1e-12, ermgbb13 * 1e-12], fmt="^", color="b", mec="b", label=r"Becker-Bolton+13", capsize=5
        # )
        plt.errorbar(
            zdal18, gamdal18 * 1e-12, yerr=[erpdal18 * 1e-12, ermdal18 * 1e-12], fmt="*", color="m", mec="m", label=r"D'Aloisio+18", capsize=5
        )


def readAscii(filename: str) -> Any:
    data = ascii.read(getDataFile("ionizationRate/" + filename))
    return data.to_pandas().values


def logToLin(logValues: np.ndarray, logErrorsLower: np.ndarray, logErrorsUpper: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    linValues = 10.0**logValues
    minValues = 10.0 ** (logValues - logErrorsLower)
    maxValues = 10.0 ** (logValues + logErrorsUpper)
    return linValues, linValues - minValues, maxValues - linValues
