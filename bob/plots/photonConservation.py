import numpy as np
import matplotlib.pyplot as plt
import astropy.units as pq
from bob.postprocessingFunctions import MultiSetFn
from bob.result import Result
from bob.multiSet import MultiSet
from bob.plots.timePlots import addTimeArg
from bob.util import getArrayQuantity

from bob.plotConfig import PlotConfig
import polars as pl

def makeQ(series):
    return pq.dimensionless_unscaled * np.array(series)

class PhotonConservation(MultiSetFn):
    def __init__(self, config: PlotConfig) -> None:
        config.setDefault("quotient", None)
        super().__init__(config)
        config.setDefault("xUnit", "1.0", override=True)
        config.setDefault("yUnit", "1.0", override=True)
        config.setDefault("xLabel", "$N_{\\mathrm{cell}}$")
        config.setDefault("yLabel", "$\\xi(N_{\\mathrm{cell}})$")

    def post(self, sims: MultiSet) -> Result:
        if len(sims) > 1:
            raise NotImplementedError("To do this, properly label sims in the df i guess")
        sims = next(iter(sims))

        df = pl.concat([getDf(sim) for sim in sims])
        return df

    def plot(self, plt: plt.axes, df: Result) -> None:
        df = df.with_columns(pl.Series(name="final_value", values= df["final_value"] / 2**2))
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        self.setupLinePlot()
        labels = self.getLabels()
        colors = self.getColors()
        plt.ylim(0.0, 0.10)
        # ITS FUCKING MATPLOTLIB TIME AGAIN. DONT YOU JUST LOVE IT? EVERYBODY PUT YOUR HANDS UP IN THE AIR
        ax.set_xscale("log")
        plt.tick_params(
            axis='x',          # changes apply to the x-axis
            which='minor',      # both major and minor ticks are affected
            bottom=False,      # ticks along the bottom edge are off
            top=False,         # ticks along the top edge are off
            labelbottom=False) # labels along the bottom edge are off
        resolutions = [16, 32, 64, 128]
        ax.set_xticks(resolutions, [f"${resolution}^3$" for resolution in resolutions])
        for (color, timestep) in zip(colors, [0.00002, 0.00005, 0.0001, 0.0002, 0.0004, 0.0008]):
            label = f"${int(timestep * 1000000)} \; \\mathrm{{yr}}$"
            print(label)
            sub = df.filter(pl.col("dt") == timestep)
            df1 = sub.filter(pl.col("limiter") == True)
            df2 = sub.filter(pl.col("limiter") == False)
            print(df1, df2)
            self.addLine(makeQ(df1["resolution"]), makeQ(df1["final_value"]), label=label, color= color)
            self.addLine(makeQ(df2["resolution"]), makeQ(df2["final_value"]), label="", color= color, linestyle="--")
        self.addLine(makeQ([]), makeQ([]), label="Limiter", color= "black")
        self.addLine(makeQ([]), makeQ([]), label="No Limiter", color= "black", linestyle="--")
        l = plt.legend(ncol = 2, labelspacing=0.15, title="$\\Delta t_{\\mathrm{max}}$", loc=(0, 0.66), columnspacing=0.8)
        l.get_title().set_position((-100, 0)) # -10 is a guess

def getDf(sim):
    with sim.comovingUnits() as _:
        df = sim.get_timeseries_as_dataframe("lost_photons_fraction", 1.0)
        n = sim.params["sweep"]["num_timestep_levels"]
        final_value = df.top_k(1, by="time")["value"]
        myr_in_s = (1.0 * pq.Myr).to_value(pq.s)
        resolution = int(sim.params["input"]["paths"][0].replace("ics/", "").replace(".hdf5", ""))
        limiter = sim.params["sweep"]["limit_absorption"]

        dt = pq.Quantity(sim.params["sweep"]["max_timestep"]).to_value(pq.s) / myr_in_s
        df = pl.DataFrame({
            "n": n,
            "dt": dt,
            "resolution": resolution,
            "final_value": final_value,
            "limiter": limiter
            })
        print(df)
        return df

class PhotonConservationN(PhotonConservation):
    def __init__(self, config: PlotConfig) -> None:
        config.setDefault("quotient", None)
        config.setDefault("xUnit", "1.0", override=True)
        config.setDefault("yUnit", "1.0", override=True)
        config.setDefault("xLabel", "n")
        config.setDefault("yLabel", "$\\xi(n)$")
        super().__init__(config)

    def post(self, sims: MultiSet) -> Result:
        if len(sims) > 1:
            raise NotImplementedError("To do this, properly label sims in the df i guess")
        sims = next(iter(sims))

        df = pl.concat([getDf(sim) for sim in sims])
        return df

    def plot(self, plt: plt.axes, df: Result) -> None:
        df = df.with_columns(pl.Series(name="final_value", values= df["final_value"] / 2**2))
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        self.setupLinePlot()
        labels = self.getLabels()
        colors = self.getColors()
        plt.ylim(0.0, 0.05)
        # ITS FUCKING MATPLOTLIB TIME AGAIN. DONT YOU JUST LOVE IT? EVERYBODY PUT YOUR HANDS UP IN THE AIR
        plt.tick_params(
            axis='x',          # changes apply to the x-axis
            which='minor',      # both major and minor ticks are affected
            bottom=False,      # ticks along the bottom edge are off
            top=False,         # ticks along the top edge are off
            labelbottom=False) # labels along the bottom edge are off
        ns = [1, 2, 3, 4, 5, 6, 7]
        ax.set_xticks(ns)
        for (color, timestep) in zip(colors, [0.000025, 0.00005, 0.0001, 0.0002, 0.0004]):
            label = f"${int(timestep * 1000000)} \; \\mathrm{{yr}}$"
            print(label)
            sub = df.filter(pl.col("dt") == timestep)
            df1 = sub.filter(pl.col("limiter") == True)
            df2 = sub.filter(pl.col("limiter") == False)
            print(df1, df2)
            self.addLine(makeQ(df1["n"]), makeQ(df1["final_value"]), label=label, color= color)
            self.addLine(makeQ(df2["n"]), makeQ(df2["final_value"]), label="", color= color, linestyle="--")
        plt.legend(title="$\\Delta t_{\\mathrm{max}}$")
