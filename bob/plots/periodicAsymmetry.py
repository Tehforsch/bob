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
                sourcePosX = coords[np.where(snap.source() > 0)][0][0]
                epsilon = sourcePosX
                L = sim.boxSize()
                print(L, epsilon)
                xcoord = np.dot(coords, np.array([1.0, 0.0, 0.0]))
                right_mask = np.logical_and(xcoord < L / 2 + epsilon, xcoord > epsilon)
                right_of_source = np.where(right_mask)
                left_of_source = np.where(np.logical_not(right_mask))
                print(right_of_source, left_of_source)
                print(np.mean(coords[right_of_source], axis=0) / L)
                print(np.mean(coords[left_of_source], axis=0) / L)
                left = np.mean(data[left_of_source])
                right = np.mean(data[right_of_source])
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
        sns.set_palette("PuBuGn_d")
        sns.lineplot(x=df["n"], y=df["rel. error"], hue=df[delta_t_key], linewidth=1.2)
