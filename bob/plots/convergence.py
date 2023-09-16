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
                data = list(sim.get_ionization_data())
                finalFraction = data[-1][1]
                converged = abs(finalFraction - convergedFraction) < ERROR_THRESHOLD
                num_particles = sim.params["1d"]["num_particles"]
                flux = pq.Quantity(sim.params["1d"]["photon_flux"])
                number_density = pq.Quantity(sim.params["1d"]["number_density"])
                length_box = 1.0 * pq.Mpc
                length_cell = length_box / num_particles
                timescale = length_cell * number_density / flux
                subdf = pl.DataFrame(
                    {
                        "dt[kyr]": pq.Quantity(sim.params["sweep"]["max_timestep"]).to_value(pq.kyr),
                        "num_levels": sim.params["sweep"]["num_timestep_levels"],
                        "num_particles": num_particles,
                        "threshold": pq.Quantity(sim.params["sweep"]["significant_rate_threshold"]).value,
                        "timescale[kyr]": timescale.to_value(pq.kyr),
                        "converged": converged,
                        "ratio": timescale.to_value(pq.kyr) / pq.Quantity(sim.params["sweep"]["max_timestep"]).to_value(pq.kyr),
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
        print(result)
        plt.clf()
        g = sns.relplot(
            data=result, x="timescale[kyr]", y="ratio", hue="num_levels", row="threshold", kind="line", linewidth=1.2, height=2, aspect=1.5, legend=True
        )
        g.tight_layout()
        # plt.xlim((10**-1.2, 1e4))
        # plt.ylim((0.0, 1.0))
        plt.xscale("log")
        plt.yscale("log")
        # self.addLine(pq.s * np.array([1,2,3]), pq.s * np.array([4,5,6]))
