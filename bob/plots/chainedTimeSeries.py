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
        self.config.setDefault("xLim", None)
        self.config.setDefault("yLim", None)

    def ylabel(self) -> str:
        return "$T [\\mathrm{K}]$"

    def post(self, sims: MultiSet) -> Result:
        if len(sims) > 1:
            raise NotImplementedError("To do this, properly label sims in the df i guess")
        df = pl.concat(
            [pl.concat([sim.get_timeseries_as_dataframe(self.config["series"], pq.Unit(self.config["yUnit"])) for sim in sims]) for sims in sims]
        )
        return df

    def plot(self, plt: plt.axes, result: Result) -> None:
        print(result)
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.set_yscale("log")
        self.setupLinePlot()
        labels = self.getLabels()
        plt.plot(result["redshift"], result["value"], linestyle="-")

class LuminosityOverTimeSubsweep(ChainedTimeSeries):
    def __init__(self, config: PlotConfig) -> None:
        config.setDefault("yUnit", "s^-1 ckpc^-3 h^-3", override=True)
        config.setDefault("yLabel", "$L / V [s^{-1} ckpc^{-3} h^{-3}]$")
        super().__init__(config)
        self.config["series"] = "total_luminosity"

    def post(self, sims: MultiSet) -> Result:
        if len(sims) > 1:
            raise NotImplementedError("To do this, properly label sims in the df i guess")
        sims = next(iter(sims))
        def getDf(sim):
            L = sim.comovingBoxSize()
            # uglily multiply by s so we get the time factor out. i dont like astropy units 
            print(L)
            one_over_vol = sim.convertComovingUnit(self.config["yUnit"] + " s", L**-3)
            print(one_over_vol)
            df = sim.get_timeseries_as_dataframe(self.config["series"], 1 / pq.s)
            return df.with_columns((pl.col("value") * pl.lit(one_over_vol.value)).alias("value"))
        df = pl.concat([getDf(sim) for sim in sims])
        return df
    
