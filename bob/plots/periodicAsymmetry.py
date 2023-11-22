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

delta_t_key = "$\\Delta t_{\\text{max}} \\; [\\mathrm{kyr}]$"


class PeriodicAsymmetry(MultiSetFn):
    def __init__(self, config: PlotConfig):
        super().__init__(config)

    def post(self, simSets: MultiSet) -> Result:
        dfs = []
        for sims in simSets:
            for sim in sims:
                snap = sim.snapshots[-1]
                data = snap.ionized_hydrogen_fraction()
                coords = snap.position()
                L = sim.boxSize()
                left = np.where(np.dot(coords, np.array([1.0, 0.0, 0.0])) < L / 2)
                right = np.where(np.dot(coords, np.array([1.0, 0.0, 0.0])) > L / 2)
                print(np.mean(coords[left], axis=0) / L)
                print(np.mean(coords[right], axis=0) / L)
                left = np.mean(data[left])
                right = np.mean(data[right])
                subdf = pl.DataFrame(
                    {
                        "rel. error": [abs(left - right) / (left + right)],
                        "n": sim.params["sweep"]["num_timestep_levels"],
                        delta_t_key: pq.Quantity(sim.params["sweep"]["max_timestep"]).to_value(pq.kyr),
                    }
                )
                dfs.append(subdf)
        df = pl.concat(dfs)
        return df

    def plot(self, plt: plt.axes, df: Result) -> None:
        sns.lineplot(x=df["n"], y=df["rel. error"], hue=df[delta_t_key], linewidth=1.2)
