import argparse
import re
import itertools
from typing import List, Tuple
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.ticker

from astropy.cosmology import z_at_value

from bob.simulation import Simulation
from bob.postprocessingFunctions import MultiSetFn, addToList
from bob.result import Result
from bob.multiSet import MultiSet


class IonizationData:
    def __init__(self) -> None:
        self.data: List[List[float]] = []

    def setNeutralFractions(self) -> None:
        self.neutralVolumeAv = 1.0 - self.volumeAv
        self.neutralMassAv = 1.0 - self.massAv

    def fromSims(self, sims: List[Simulation]) -> "IonizationData":
        for sim in sims:
            assert sim.params.get("ComovingIntegrationOn") == 1
            cosmology = sim.getCosmology()
            # "Time" is just the scale factor here. To make sure that this is true, check that ComovingIntegrationOn is 1
            regex = re.compile("Time ([0-9.+]+): Volume Av. H ionization: ([0-9.+]+), Mass Av. H ionization: ([0-9.+]+)")
            for line in sim.log:
                match = regex.match(line)
                if match is not None:
                    self.data.append([float(x) for x in match.groups()])

        self.scale_factor = np.array([d[0] for d in self.data])
        self.volumeAv = np.array([d[1] for d in self.data])
        self.massAv = np.array([d[2] for d in self.data])
        self.redshift = np.array([z_at_value(cosmology.scale_factor, sf) for sf in self.scale_factor])
        self.setNeutralFractions()
        return self

    def fromArray(self, arr: np.ndarray) -> "IonizationData":
        self.scale_factor = arr[0, :]
        self.redshift = arr[1, :]
        self.volumeAv = arr[2, :]
        self.massAv = arr[3, :]
        self.setNeutralFractions()
        return self

    def toArray(self) -> np.ndarray:
        result = np.zeros((4, self.scale_factor.shape[0]))
        result[0, :] = self.scale_factor
        result[1, :] = self.redshift
        result[2, :] = self.volumeAv
        result[3, :] = self.massAv
        return result


class Ionization(MultiSetFn):
    def post(self, args: argparse.Namespace, simSets: MultiSet) -> Result:
        self.labels = simSets.labels
        return Result([IonizationData().fromSims(sims).toArray() for sims in simSets])

    def plot(self, plt: plt.axes, result: Result) -> None:
        ionizationDataList = [IonizationData().fromArray(arr) for arr in result.arrs]
        plt.style.use("classic")
        colors = ["b", "r", "g", "purple", "brown", "orange"]
        linAx, logAx = setupIonizationPlot()

        self.addConstraintsToAxis(linAx)
        self.addConstraintsToAxis(logAx)

        for (ionizationData, color) in zip(ionizationDataList, itertools.cycle(colors)):
            self.plotResultsToAxis(ionizationData, linAx, color)
            self.plotResultsToAxis(ionizationData, logAx, color)
        # add legend labels
        for (label, color) in zip(self.labels, colors):
            linAx.plot([], [], color=color, label=label, linewidth=3)
        linAx.plot([], [], label="Volume av.", linestyle="-", linewidth=3, color="black")
        linAx.plot([], [], label="Mass av.", linestyle="--", linewidth=3, color="black")
        plt.legend(loc=(0, -0.2))

    def plotResultsToAxis(self, data: IonizationData, ax: plt.axes, color: str) -> None:
        ax.plot(data.redshift, data.neutralVolumeAv, linewidth=3, color=color, linestyle="-")
        ax.plot(data.redshift, data.neutralMassAv, linewidth=3, color=color, linestyle="--")

    def addConstraintsToAxis(self, ax: plt.axes) -> None:
        fan06 = np.reshape(
            [
                6.099644128113878,
                0.0004359415240334025,
                5.850533807829182,
                0.00012089973216672045,
                5.649466192170818,
                0.00008641259285077239,
                5.45017793594306,
                0.00006667934792772513,
                5.250889679715303,
                0.00006726593764703922,
                5.032028469750889,
                0.00005511182476220595,
            ],
            (6, 2),
        )
        fanEryUp06 = np.abs(np.asarray([9.975, 3.457, 1.77, 1.238, 1.238, 0.8796]) * 1e-4 - fan06[:, 1])
        fanEryDw06 = np.abs(np.asarray([2.22, 1.48, 0.688, 0.634, 0.548, 0.539]) * 1e-4 - fan06[:, 1])

        ax.errorbar([0], [0], yerr=[0], label=r"Ly$\alpha$ forest, Fan+06", c="k", fmt="x", capsize=5)

        bosman21_xHI = np.asarray(
            [
                [5, 5.1, 5.2, 5.3, 5.4, 5.5, 6.5, 5.7, 5.8],
                [3.02, 3.336, 3.636, 3.598, 3.498, 4.328, 5.627, 6.544, 7.087],
                [0.058, 0.164, 0.095, 0.145, 3.332, 4.016, 4.630, 5.99, 6.401],
                [0.23, 0.064, 0.131, 0.566, 3.332, 4.016, 4.630, 5.99, 6.401],
                [False, False, False, False, True, True, True, True, True],
            ]
        )  # z, value, lower lim, upper lim, (bool) lower limit?

        ax.errorbar([0], [0], yerr=[0], c="green", fmt="x", label=r"Ly$\alpha$ forest, Bosman+21", capsize=5)

        ax.errorbar([0], [0], yerr=[0], c="grey", fmt="x", label=r"Ly$\alpha$ forest, Becker+15", capsize=5)

        mason18 = [0.59, 7]
        masonUp18 = [0.11]
        masonDw18 = [0.15]

        ax.errorbar(mason18[1] + 0.05, mason18[0], ([masonDw18, masonUp18]), 0, c="brown", fmt="D", capsize=5)

        ono12 = 0.75
        ono12z = 7
        ono12err = 0.15

        ax.errorbar(ono12z, ono12, yerr=ono12err, color="brown", fmt="D", capsize=5)

        schenker13 = [0.39, 0.65]
        schenker13z = [7, 8]
        schenker13up = [0.09, 0.1]
        schenker13dw = [0.08, 0.1]

        ax.errorbar(schenker13z, schenker13, yerr=[schenker13dw, schenker13up], color="brown", fmt="D", capsize=5, lolims=[False, True])

        petericci2014 = 0.51
        petericci2014z = 7
        petericci2014err = [[0], [0.1]]

        ax.errorbar(petericci2014z - 0.05, petericci2014, yerr=petericci2014err, color="brown", fmt="D", lolims=True, capsize=5)

        zhoag19 = 7.6
        zhoag19m = [0.6]
        zhoag19p = [0.6]
        xhihoag19 = 1 - 0.12
        ermxhihoag19 = [0.05]
        erpxhihoag19 = [0.1]
        ax.errorbar(zhoag19, xhihoag19, xerr=[zhoag19m, zhoag19p], yerr=[ermxhihoag19, erpxhihoag19], color="brown", capsize=5, fmt="D")

        tilvi14 = 0.3
        tilvi14z = 8
        tilvi14err = [[0], [0.1]]

        ax.errorbar(tilvi14z + 0.05, tilvi14, yerr=tilvi14err, color="brown", fmt="D", label="LAE fraction", lolims=True, capsize=5)

        mortlock11 = 0.1
        mortlock11z = 7.1
        mortlock11err = [[0], [0.1]]

        ax.errorbar(mortlock11z, mortlock11, mortlock11err, color="darkolivegreen", fmt="s", lolims=True, capsize=5)

        schroeder13 = 0.1
        schroeder13z = 6.2
        schroeder13err = [[0], [0.1]]

        ax.errorbar(schroeder13z, schroeder13, yerr=schroeder13err, color="darkolivegreen", fmt="s", lolims=True, capsize=5)

        banados18 = 0.33
        banados18z = 7.09
        banados18err = [[0], [0.1]]

        ax.errorbar(banados18z, banados18, yerr=banados18err, color="darkolivegreen", fmt="s", lolims=True, capsize=5)

        durovcikova19 = [0.25, 0.60]
        durovcikova19z = [7.0851, 7.5413]
        durovcikova19err = [0.05, 0.11]

        ax.errorbar(durovcikova19z, durovcikova19, yerr=durovcikova19err, color="darkolivegreen", fmt="s", label="QSO damping wings", capsize=5)

        wang21_xhi = 0.7
        wang21_z = 7
        wang21_xhi_dw = 0.23
        wang21_xhi_up = 0.2

        ax.errorbar([wang21_z - 0.05], [wang21_xhi], yerr=[[wang21_xhi_dw], [wang21_xhi_up]], color="darkolivegreen", fmt="s", capsize=5)

        totani16 = 0.06
        totani16z = 5.91

        ax.errorbar(totani16z, totani16, 0, 0, marker="o", color="darkcyan", capsize=5, linestyle="none")
        ax.errorbar(0.0, 0.0, 0.0, 0.0, marker="o", color="darkcyan", label="GRB damping wing", capsize=5, linestyle="none")

        ouchi10 = [0.2, 6.6]
        ouchi10_err = 0.2

        ax.errorbar(
            ouchi10[1] + 0.05,
            (ouchi10[0] + ouchi10_err),
            ouchi10_err * 0.5,
            0,
            color="purple",
            fmt="P",
            uplims=True,
            label=r"Ly$\alpha$ LF",
            capsize=5,
        )

        mcgreer15 = [0.11, 0.10]
        mcgreer15z = [5.9, 5.6]

        ax.errorbar(mcgreer15z, mcgreer15, 0.05, color="goldenrod", fmt="p", linestyle="none", uplims=True, label=r"Dark pixel fraction", capsize=5)

        ax.errorbar(
            bosman21_xHI[0],
            bosman21_xHI[1] * 1e-5,
            yerr=[bosman21_xHI[2] * 1e-5, bosman21_xHI[3] * 1e-5],
            lolims=bosman21_xHI[-1],
            c="green",
            fmt="x",
            capsize=5,
        )  # ,label=r'Ly$\alpha$ forest, Bosman+21')

        becker_2015_xHI, becker_2015_low, becker_2015_high = getBeckerData2015()
        ax.errorbar(
            becker_2015_xHI[:, 0] - 0.05,
            becker_2015_xHI[:, 1] * 1e-5,
            yerr=[(becker_2015_xHI[:, 1] - becker_2015_low) * 1e-5, (becker_2015_high - becker_2015_xHI[:, 1]) * 1e-5],
            c="grey",
            fmt="x",
            capsize=5,
        )  # ,label=r'Ly$\alpha$ forest, Becker+15')
        ax.errorbar(fan06[:, 0], (fan06[:, 1]), ([fanEryDw06, fanEryUp06]), c="k", fmt="x", capsize=5)  # ,label=r'Ly$\alpha$ forest, Fan+06')

        ax.errorbar(mcgreer15z, mcgreer15, 0.05, color="goldenrod", fmt="p", linestyle="none", uplims=True, capsize=5)

        ax.errorbar(mortlock11z, mortlock11, color="darkolivegreen", fmt="s", capsize=5)
        ax.errorbar(schroeder13z, schroeder13, color="darkolivegreen", fmt="s", capsize=5)


def setupIonizationPlot() -> Tuple[plt.axes, plt.axes]:
    label_font_size = 17
    tics_label_size = 15
    n_split = 4
    minXHI = 1e-7
    maxXHI = 1
    splitXHI = 1e-1
    minRedshift = 4.2
    maxRedshift = 10

    fig = plt.figure(figsize=(10, 10), tight_layout=True)
    grid_spec = gridspec.GridSpec(n_split, 1, hspace=0)
    logAx = fig.add_subplot(grid_spec[-1, :])
    linAx = fig.add_subplot(grid_spec[:-1, :])

    linAx.set_xlim(minRedshift, maxRedshift)
    linAx.set_ylim(splitXHI, 1.0)

    logAx.set_xlim(minRedshift, maxRedshift)
    logAx.set_ylim(minXHI, splitXHI)

    linAx.invert_xaxis()
    logAx.invert_xaxis()

    linAx.grid("on")
    logAx.grid("on")
    logAx.set_yscale("log")

    linAx.tick_params(which="both", direction="in", top="on", right="on", bottom="off", labelbottom=False, labelsize=tics_label_size)
    linAx.tick_params(axis="y", pad=+18, labelbottom="off")
    logAx.tick_params(which="major", direction="in", top="off", right="on", bottom="on", labelsize=tics_label_size)
    logAx.tick_params(which="minor", direction="in", top="off", right="off", bottom="off", left="off")

    yLabelPositionX = 4.0
    yLabelPositionY = 2.0 / (n_split + 1)
    plt.text(yLabelPositionX, yLabelPositionY, "xHI", rotation=90, ha="center", fontsize=label_font_size)
    logAx.set_xlabel("z", fontsize=label_font_size)

    step = 0.1
    yticksLin = np.arange(splitXHI + step, maxXHI + step, step)
    linAx.set_yticks(yticksLin)
    linAx.set_yticklabels(["{:.1f}".format(x) for x in yticksLin])

    locmaj = matplotlib.ticker.LogLocator(base=10, numticks=int(abs(np.log10(splitXHI) - np.log10(1e-5)) + 1))
    logAx.yaxis.set_major_locator(locmaj)

    linAx.spines["bottom"].set_visible(False)
    logAx.spines["top"].set_visible(False)

    return linAx, logAx


def getBeckerData2015() -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    becker_2015_raw = np.asarray(
        [
            3.91779e0,
            8.92495e-1,
            4.12493e0,
            1.04970e0,
            4.33202e0,
            1.04970e0,
            4.54258e0,
            1.49594e0,
            4.74988e0,
            2.15010e0,
            4.95876e0,
            2.55071e0,
            5.16594e0,
            2.79919e0,
            5.37482e0,
            3.20487e0,
            5.58532e0,
            3.50406e0,
            5.79265e0,
            4.20385e0,
            3.91606e0,
            6.79513e-1,
            4.12485e0,
            7.86004e-1,
            4.33194e0,
            7.86004e-1,
            4.54080e0,
            1.13590e0,
            4.74971e0,
            1.63793e0,
            4.95858e0,
            1.98276e0,
            5.16574e0,
            2.20081e0,
            5.37461e0,
            2.57099e0,
            5.58345e0,
            2.84990e0,
            5.79240e0,
            3.45842e0,
            3.91623e0,
            1.19168e0,
            4.12505e0,
            1.38945e0,
            4.33379e0,
            1.38945e0,
            4.54108e0,
            1.97769e0,
            4.75011e0,
            2.81947e0,
            4.95902e0,
            3.31136e0,
            5.16619e0,
            3.57505e0,
            5.37509e0,
            4.01623e0,
            5.58394e0,
            4.32049e0,
            5.79295e0,
            5.12677e0,
        ]
    ).reshape((30, 2))

    becker_2015_xHI = becker_2015_raw[:10, :]
    becker_2015_low = becker_2015_raw[10:20, 1]
    becker_2015_high = becker_2015_raw[20:, 1]
    return becker_2015_xHI, becker_2015_low, becker_2015_high


addToList("ionization", Ionization())
