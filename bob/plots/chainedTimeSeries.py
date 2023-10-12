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
        self.config.setDefault("xUnit", "1.0")
        self.config.setDefault("yUnit", "1.0 K")
        self.config.setDefault("xLabel", "z")
        self.config.setDefault("yLabel", "$T [K]$")

    def ylabel(self) -> str:
        return "$T [\\mathrm{K}]$"

    def post(self, sims: MultiSet) -> Result:
        if len(sims) > 1:
            raise NotImplementedError("To do this, properly label sims in the df i guess")
        df = pl.concat(
            [pl.concat([sim.get_timeseries_as_dataframe(self.config["series"], pq.Quantity(self.config["yUnit"])) for sim in sims]) for sims in sims]
        )
        return df

    def plot(self, plt: plt.axes, result: Result) -> None:
        print(result)
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.set_yscale("log")
        self.setupLinePlot()
        labels = self.getLabels()
        self.addLine(
            pq.Quantity(result["redshift"]) * pq.Quantity(self.config["xUnit"]),
            pq.Quantity(result["value"]) * pq.Quantity(self.config["yUnit"]),
            linestyle="-",
        )
        # plt.legend(loc=self.config["legend_loc"])
