from typing import List

import numpy as np
import matplotlib.pyplot as plt
import astropy.units as pq

from bob.result import Result
from bob.snapshot import Snapshot
from bob.basicField import BasicField
from bob.simulation import Simulation
from bob.temperature import Temperature
from bob.plotConfig import PlotConfig
from bob.plots.meanFieldOverTime import MeanFieldOverTime


class ChainedTimeSeries(MultiSetFn):
    def __init__(self, config: PlotConfig) -> None:
        super().__init__(config)
        self.config.setDefault("series", "mass_av_temperature")

    def ylabel(self) -> str:
        return "$T [\\mathrm{K}]$"

    @abstractmethod
    def post(self, sims: MultiSet) -> Result:
        for sims in sims:
            for sim in sims:
                print(sim)
                print(sim.get_timeseries(self.config["series"]))

    def plot(self, plt: plt.axes, result: Result) -> None:
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.set_yscale("log")
        self.setupLinePlot()
        labels = self.getLabels()
        colors = self.getColors()
        for redshift, volumeRate, massRate, color, label in zip(result.redshift, result.volumeAvRate, result.massAvRate, colors, labels):
            self.addLine(redshift, volumeRate, color=color, linestyle="-", label=label)
            self.addLine(redshift, massRate, color=color, linestyle="--", label="")
        plt.plot([], [], color="black", linestyle="-", label="volume av.")
        plt.plot([], [], color="black", linestyle="--", label="mass av.")
        self.addConstraints()
        plt.legend(loc=self.config["legend_loc"])
