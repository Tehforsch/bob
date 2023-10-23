from typing import List, Tuple, Callable
import numpy as np
import matplotlib.pyplot as plt
import astropy.units as u
import polars as pl

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
            assert(len(sims) == 1)
            sim = sims[0]
            resolution = int(sim.params["input"]["paths"][0].replace("ics/", "").replace(".hdf5", ""))
            df = sim.get_timeseries_as_dataframe("hydrogen_ionization_mass_average", 1.0, "Myr")
            L = u.Quantity(sim.params["box_size"]).to_value(u.kpc)
            pi = 3.1415
            print(L)
            return df.with_columns(
                [
                    pl.lit(resolution).alias("resolution"),
                    ((3.0 * L**3 / (4.0 * pi) * pl.col("value")) ** (1.0 / 3.0)).alias("radius"),
                ])
        return pl.concat([getDf(sims) for sims in sims])

    def plot(self, plt: plt.axes, df: Result) -> None:
        print(df)
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        self.setupLinePlot()
        labels = self.getLabels()
        for (resolution, df) in df.groupby(pl.col("resolution")):
            xd =u.Quantity(df["time"])  / u.Quantity(self.config["recombination_time"]).to_value(u.Myr)
            yd =u.Quantity(df["radius"]) * self.yUnit() / u.Quantity(self.config["stroemgren_radius"]).to_value(u.kpc)
            self.addLine(
                xd,
                yd ,
                
                linestyle="-",
            )
        # plt.legend(loc=self.config["legend_loc"])
