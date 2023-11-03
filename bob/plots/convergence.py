import seaborn as sns
import polars as pl
import numpy as np
import astropy.units as pq
import matplotlib.pyplot as plt

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
        ERROR_THRESHOLD = 0.01
        dfs = []
        for sims in simSets:
            for sim in sims:
                print(sim.folder)
                data = sim.get_timeseries("hydrogen_ionization_mass_average")
                finalFraction = data.value[-1]
                converged = abs(finalFraction - convergedFraction) < ERROR_THRESHOLD
                num_particles = sim.params["1d"]["num_particles"]
                flux = pq.Quantity(sim.params["1d"]["photon_flux"])
                number_density = pq.Quantity(sim.params["1d"]["number_density"])
                length_box = 1.0 * pq.Mpc
                length_cell = length_box / num_particles
                timescale = length_cell * number_density / flux
                runtime = sim.get_performance_data()["Stages::Sweep"]["total"]
                subdf = pl.DataFrame(
                    {
                        "dt[kyr]": pq.Quantity(sim.params["sweep"]["max_timestep"]).to_value(pq.kyr),
                        "num_levels": sim.params["sweep"]["num_timestep_levels"],
                        "num_particles": num_particles,
                        "threshold": pq.Quantity(sim.params["sweep"]["significant_rate_threshold"]).value,
                        "timescale[kyr]": timescale.to_value(pq.kyr),
                        "converged": converged,
                        "ratio": timescale.to_value(pq.kyr) / pq.Quantity(sim.params["sweep"]["max_timestep"]).to_value(pq.kyr),
                        "runtime[s]": pq.Quantity(runtime).to_value(pq.s),
                    }
                )
                dfs.append(subdf)
        df = pl.concat(dfs)
        df = df.filter(pl.col("converged") == 1)
        dfs = df.partition_by(["num_levels", "num_particles", "threshold"])
        dfs = [df.top_k(1, by="dt[kyr]") for df in dfs]
        df = pl.concat(dfs)
        return df

    def plot(self, plt: plt.axes, result: Result) -> None:
        plt.clf()
        result = result.rename({"num_levels": "n"})
        print(result)

        fig=plt.figure()
        ax1 = plt.subplot(211)
        ax2 = plt.subplot(212, sharex = ax1)
        fig.set_size_inches(3, 4)

        ax = sns.lineplot(
            ax=ax1,
            data=result,
            x="num_particles",
            y="dt[kyr]",
            hue="n",
            linewidth=1.2,
            legend=True,
        )
        ax.set(ylabel="$\\Delta t [\\text{kyr}]$", xscale="log", yscale="log", xticklabels=[], xlabel=None)

        ax.set_xticklabels([])
        print(ax.get_xticks())
        ax.set(xticklabels=[])
        ax = sns.lineplot(
            ax=ax2,
            data=result,
            x="num_particles",
            y="runtime[s]",
            hue="n",
            linewidth=1.2,
            legend=False,
        )
        ax.set(xlabel="N", ylabel="\\text{runtime} [\\text{s}]", xscale="log", yscale="log", ylim=[0.01,1000])
