from typing import List

import numpy as np
import matplotlib.pyplot as plt
import astropy.units as pq
import polars as pl

from bob.result import Result
from bob.snapshot import Snapshot
from bob.basicField import BasicField
from bob.simulation import Simulation
from bob.temperature import Temperature
from bob.plotConfig import PlotConfig
from bob.plots.meanFieldOverTime import MeanFieldOverTime
from bob.postprocessingFunctions import MultiSetFn
from bob.multiSet import MultiSet


class ChainedTimeSeries(MultiSetFn):
    def __init__(self, config: PlotConfig) -> None:
        config.setDefault("quotient", None)
        super().__init__(config)
        self.config.setDefault("series", "temperature_mass_average")
        self.config.setDefault("yUnit", "1.0 K")

    def ylabel(self) -> str:
        return "$T [\\mathrm{K}]$"

    def post(self, sims: MultiSet) -> Result:
        df = pl.concat([pl.concat([sim.get_timeseries_as_dataframe(self.config["series"], pq.Quantity(self.config["yUnit"])) for sim in sims]) for sims in sims])
        return df

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
