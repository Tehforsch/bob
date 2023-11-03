import seaborn as sns
import polars as pl
import numpy as np
import astropy.units as pq
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter, NullFormatter
import matplotlib

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
                        "runtime[s]": pq.Quantity(runtime).to_value(pq.s),
                    }
                for (i, threshold) in enumerate(error_thresholds):
                    converged = abs(finalFraction - convergedFraction) < threshold
                    entries[f"converged_{i}"] = converged
                subdf = pl.DataFrame(entries)
                dfs.append(subdf)
        df = pl.concat(dfs)
        return df

    def plot(self, plt: plt.axes, df: Result) -> None:
        plt.clf()
        df = df.rename({"num_levels": "n"})
        df = df.filter(pl.col("converged_1") == 1)
        dfs = df.partition_by(["num_levels", "num_particles", "threshold"])
        dfs = [df.top_k(1, by="dt[kyr]") for df in dfs]
        df = pl.concat(dfs)
        print(df)

        fig=plt.figure()
        ax1 = plt.subplot(211)
        ax2 = plt.subplot(212, sharex = ax1)
        fig.set_size_inches(3, 4)

        xlim=[10,10240]

        ax = sns.lineplot(
            ax=ax1,
            data=df,
            x="num_particles",
            y="dt[kyr]",
            hue="n",
            linewidth=1.2,
            legend=True,
        )
        ax1.set(ylabel="$\\Delta t [\\text{kyr}]$", xscale="log", yscale="log", xlabel=None, xticks=[], xlim=xlim)
        ax.xaxis.set_minor_formatter(NullFormatter()) # GOD I FUCKING HATE MATPLOTLIB WHY IS THIS SO HARD TO FIND

        ax = sns.lineplot(
            ax=ax2,
            data=df,
            x="num_particles",
            y="runtime[s]",
            hue="n",
            linewidth=1.2,
            legend=False,
        )
        ax.set(xlabel="N", ylabel="\\text{runtime} [\\text{s}]", xscale="log", ylim=[0.0,15], xlim=xlim)
        ax.xaxis.set_minor_formatter(NullFormatter()) # GOD I FUCKING HATE MATPLOTLIB WHY IS THIS SO HARD TO FIND
