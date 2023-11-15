from typing import List, Tuple, Callable
import numpy as np
import matplotlib.pyplot as plt
import astropy.units as u
import polars as pl
import itertools

from bob.basicField import BasicField
from bob.simulation import Simulation
from bob.snapshot import Snapshot
from bob.temperature import Temperature
from bob.plots.timePlots import TimePlot
from bob.plotConfig import PlotConfig
from bob.util import getArrayQuantity
from bob.result import Result
from bob.postprocessingFunctions import MultiSetFn
from bob.multiSet import MultiSet


def analyticalRTypeExpansion(t: np.ndarray) -> np.ndarray:
    return (1 - np.exp(-t)) ** (1.0 / 3)


class Expansion(MultiSetFn):
    def __init__(self, config: PlotConfig) -> None:
        super().__init__(config)
        self.config.setDefault("xUnit", "1.0")
        self.config.setDefault("yUnit", "1.0")
        self.config.setDefault("xLabel", "$t / t_{\\text{rec}}$")
        self.config.setDefault("yLabel", "$R / R_{\\text{St}}$")
        self.config.setDefault("xLim", [0, 1])
        self.config.setDefault("yLim", [0, 1])
        self.config.setDefault("stroemgren_radius", 6.79 * u.kpc)
        self.config.setDefault("recombination_time", 122.34 * u.Myr)

    def xUnit(self) -> u.Unit:
        return u.Unit(self.config["xUnit"])

    def yUnit(self) -> u.Unit:
        return u.Unit(self.config["yUnit"])

    def ylabel(self) -> str:
        return "$T [\\mathrm{K}]$"

    def post(self, sims: MultiSet) -> Result:
        def getDf(sims):
            assert len(sims) == 1
            sim = sims[0]
            resolution = int(sim.params["input"]["paths"][0].replace("ics/", "").replace(".hdf5", ""))
            df = sim.get_timeseries_as_dataframe("hydrogen_ionization_mass_average", 1.0, "Myr")
            L = u.Quantity(sim.params["box_size"]).to_value(u.kpc)
            pi = 3.1415
            return df.with_columns(
                [
                    pl.lit(resolution).alias("resolution"),
                    ((3.0 * L**3 / (4.0 * pi) * pl.col("value")) ** (1.0 / 3.0)).alias("radius"),
                ]
            )

        dfs = [getDf(sims) for sims in sims]
        print(dfs)

        def concat(dfs):
            dfs = list(dfs)
            for i in range(1, len(dfs)):
                finalTimePrev = dfs[i - 1].top_k(1, by="time")["time"]
                dfs[i] = dfs[i].with_columns((pl.col("time") + pl.lit(finalTimePrev)).alias("time"))
                print("concat")
            return pl.concat(dfs)

        # uglily concat extended runs for the same expansion
        dfs = [concat(group) for (_, group) in itertools.groupby(dfs, key=lambda df: df["resolution"][0])]
        print(dfs)

        return pl.concat(dfs)

    def plot(self, plt: plt.axes, df: Result) -> None:
        print(df)
        ax0 = plt.subplot(211)
        ax1 = plt.subplot(212, sharex=ax0)
        ax1.set_xlabel(self.config["xLabel"])
        ax0.set_ylabel(self.config["yLabel"])
        ax1.set_ylabel("Rel. error")
        ax0.set_xlim(self.config["xLim"])
        ax0.set_ylim(self.config["yLim"])
        ax1.set_ylim([0, 0.03])
        for resolution, df in df.sort("resolution").groupby(pl.col("resolution")):
            xd = u.Quantity(df["time"]) / u.Quantity(self.config["recombination_time"]).to_value(u.Myr)
            yd = u.Quantity(df["radius"]) * self.yUnit() / u.Quantity(self.config["stroemgren_radius"]).to_value(u.kpc)
            ax0.plot(xd, yd, linestyle="-", label=resolution)
            yd = error(xd, yd)
            ax1.plot(xd, yd, linestyle="-", label=resolution)
        x = np.arange(0.0, 2.0, 0.001)
        ax0.plot(x * u.Quantity(1.0), analyticalRTypeExpansion(x) * u.Quantity(1.0), linestyle="--", label="Analytical")
        ax0.legend(loc="lower right")


def error(xd, yd):
    ana = analyticalRTypeExpansion(xd)
    error = np.abs(yd - ana) / ana
    return error
