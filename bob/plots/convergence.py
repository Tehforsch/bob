import seaborn as sns
import polars as pl
import numpy as np
import astropy.units as pq
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter, NullFormatter
import matplotlib
import matplotlib.gridspec as gridspec

from bob.postprocessingFunctions import MultiSetFn
from bob.result import Result
from bob.multiSet import MultiSet
from bob.plotConfig import PlotConfig


class Convergence(MultiSetFn):
    def __init__(self, config: PlotConfig):
        super().__init__(config)
        self.config.setDefault("xLim", [1e-10, 1e10])
        self.config.setDefault("yLim", None)
        self.config.setDefault("split", True)
        self.config.setDefault("xUnit", pq.Myr)
        self.config.setDefault("yUnit", pq.Myr)

    def post(self, simSets: MultiSet) -> Result:
        convergedFraction = 0.4713
        error_thresholds = [0.1, 0.01, 0.001, 0.0001]
        dfs = []
        for sims in simSets:
            for sim in sims:
                print(sim.folder)
                data = sim.get_timeseries("hydrogen_ionization_mass_average")
                finalFraction = data.value[-1]
                num_particles = sim.params["1d"]["num_particles"]
                flux = pq.Quantity(sim.params["1d"]["photon_flux"])
                number_density = pq.Quantity(sim.params["1d"]["number_density"])
                length_box = 1.0 * pq.Mpc
                length_cell = length_box / num_particles
                timescale = length_cell * number_density / flux
                runtime = sim.get_performance_data()["Stages::Sweep"]["total"]
                entries = {
                    "dt[kyr]": pq.Quantity(sim.params["sweep"]["max_timestep"]).to_value(pq.kyr),
                    "num_levels": sim.params["sweep"]["num_timestep_levels"],
                    "num_particles": num_particles,
                    "threshold": pq.Quantity(sim.params["sweep"]["significant_rate_threshold"]).value,
                    "timescale[kyr]": timescale.to_value(pq.kyr),
                    "ratio": timescale.to_value(pq.kyr) / pq.Quantity(sim.params["sweep"]["max_timestep"]).to_value(pq.kyr),
                    "trun/n": pq.Quantity(runtime).to_value(pq.s) / num_particles,
                }
                for i, threshold in enumerate(error_thresholds):
                    converged = abs(finalFraction - convergedFraction) < threshold
                    entries[f"converged_{i}"] = converged
                subdf = pl.DataFrame(entries)
                dfs.append(subdf)
        df = pl.concat(dfs)
        return df

    def plot(self, plt: plt.axes, df: Result) -> None:
        plt.clf()
        df = df.filter(pl.col("converged_1") == 1)
        dfs = df.partition_by(["num_levels", "num_particles", "threshold"])
        dfs = [df.top_k(1, by="dt[kyr]") for df in dfs]
        df = pl.concat(dfs)
        df = df.rename({"num_levels": "n"})
        df = df.filter(pl.col("num_particles") > 100)
        df = df.filter(pl.col("n") < 7)
        print(df)

        fig = plt.figure()
        ax1 = plt.subplot(211)
        ax2 = plt.subplot(212, sharex=ax1)
        # gs1 = gridspec.GridSpec(2, 1)
        # gs1.update(wspace=0.025, hspace=0.05)
        # ax1 = plt.subplot(111)
        # ax2 = plt.subplot(222)
        plt.setp(ax1.get_xticklabels(), visible=False)
        fig.set_size_inches(3, 4)
        fig.subplots_adjust(wspace=None, hspace=0.05)

        xlim = [100, 11240]
        df = df.with_columns((pl.col("trun/n") * 1000).alias("trun/n"))
        df = df.with_row_count()
        # fix those runs where output was different
        df = df.with_columns(
            corrected_for_wrong_run = pl
            .when(pl.col("row_nr") == 30).then(pl.col("trun/n") / 2)
            .when(pl.col("row_nr") == 31).then(pl.col("trun/n") / 2)
            .when(pl.col("row_nr") == 32).then(pl.col("trun/n") / 2)
            .otherwise(pl.col("trun/n")),
        )

        axlol = sns.lineplot(
            ax=ax1,
            data=df,
            x="num_particles",
            y="dt[kyr]",
            hue="n",
            linewidth=1.2,
            legend=True,
        )

        sns.move_legend(axlol, loc='lower left', bbox_to_anchor=[0.0,-0.05])
        sns.lineplot(
            ax=ax2,
            data=df,
            x="num_particles",
            y="corrected_for_wrong_run",
            hue="n",
            linewidth=1.2,
            legend=False,
        )
        ax1.set(ylabel="$\\Delta t [\\text{kyr}]$", xscale="log", yscale="log", xlabel=None, xlim=xlim)
        ax1.xaxis.set_minor_formatter(NullFormatter())
        ax2.set(xlabel="N", ylabel="$t_{\\mathrm{run}} / N$ [ms]", xscale="log", ylim=[0.0, 2.5], xlim=xlim)
