import matplotlib.pyplot as plt
import astropy.units as pq
from astropy.io import ascii

from bob.postprocessingFunctions import MultiSetFn, addToList
from bob.result import Result
from bob.multiSet import MultiSet
from bob.plots.ionization import IonizationData
from bob.plotConfig import PlotConfig


class IonizationRate(MultiSetFn):
    def __init__(self, config: PlotConfig) -> None:
        super().__init__(config)
        self.config.setDefault("xLabel", "z")
        self.config.setDefault("yLabel", "R")
        self.config.setDefault("xUnit", pq.dimensionless_unscaled)
        self.config.setDefault("yUnit", 1 / pq.s)
        self.config.setDefault("legend_loc", "upper right")
        self.config.setDefault("yLim", [1e-18, 1e-12])

    def post(self, simSets: MultiSet) -> Result:
        result = IonizationData(simSets)
        return result

    def plot(self, plt: plt.axes, result: Result) -> None:
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
        self.addConstraints()
        plt.legend(loc=self.config["legend_loc"])

    def addConstraints(self) -> None:
        data = ascii.read(".obs/faucher-giguere2008/table1")
        [zfc08, tauafc08, taubfc08, gamfc08, e_gamfc08] = data.to_pandas().values.T
        print(zfc08)
        # lgamfc08 = gamfc08 * 1e-12
        print(e_gamfc08)
        print(gamfc08)

        # data = ascii.read("./obs/becker_bolton2013/table1")
        # d=data.to_pandas()
        # d=d.values
        # [zbb13,lgambb13,erplgbb13,ermlgbb13]=d

        # data = ascii.read("./obs/daloisio2018/table2")
        # d=data.to_pandas()
        # d=d.values
        # [zdal18,gamdal18,erpdal18,ermdal18]=d
        # lgamdal18=np.log10(gamdal18)
        # erpldal18=np.log10(gamdal18+erpdal18)-np.log10(gamdal18)
        # ermldal18=(np.log10(gamdal18-ermdal18)-np.log10(gamdal18))

        # ax.errorbar(zcal11,lgammacal11,yerr=erlgammacal11,fmt='o',color='r',mec='r',
        #             label=r"Calverley+11",capsize=5)
        plt.errorbar(zfc08, 1e-12 * gamfc08, yerr=1e-12 * e_gamfc08, fmt="s", color="g", mec="g", label=r"Faucher-Giguere+08", capsize=5)
        # ax.errorbar(zbb13,lgambb13-12.,yerr=[erplgbb13,-ermlgbb13],fmt='^',color='b',mec='b',
        #             label=r"Becker-Bolton+13",capsize=5)
        # ax.errorbar(zdal18,lgamdal18-12.,yerr=[erpldal18,-ermldal18],fmt='*',color='m',mec='m',
        #             label=r"D'Aloisio+18",capsize=5)


addToList("ionizationRate", IonizationRate)
