import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import astropy.units as pq
import polars as pl
import seaborn as sns

from bob.simulation import Simulation
from bob.snapshot import Snapshot
from bob.result import Result
from bob.plotConfig import PlotConfig
from bob.postprocessingFunctions import MultiSetFn
from bob.multiSet import MultiSet


def extend(df):
    reference = df.bottom_k(1, by="num_cores")
    reference_time = reference["runtime[s]"]
    reference_cores = reference["num_cores"]
    return df.with_columns(
        [
            (reference_time / pl.col("runtime[s]")).alias("speedup"),
            (reference_time / pl.col("runtime[s]") / (pl.col("num_cores") / reference_cores)).alias("efficiency"),
        ]
    )


class StrongScaling(MultiSetFn):
    def __init__(self, config: PlotConfig) -> None:
        super().__init__(config)
        config.setDefault("quotient", "single")
        config.setDefault("xUnit", "pc")
        config.setDefault("yUnit", "pc")
        config.setDefault("vUnit", "s^-1 cm^-3")
        config.setDefault("cLabel", "$R [\\text{s}^-1 \\text{cm}^-3]$")
        config.setDefault("xLim", [1, 8192])

    def post(self, simSets: MultiSet) -> Result:
        dfs = []
        for sims in simSets:
            assert len(sims) == 1
            sim = sims[0]
            print(sim.folder)
            perf = sim.get_performance_data()
            runtime = pq.Quantity(perf["Stages::Sweep"]["average"]).to_value(pq.s)
            num_cores = int(perf["num_ranks"])
            num_particles = int(perf["num_particles"])
            num_dirs = int(sim.params["sweep"]["directions"])
            num_levels = int(sim.params["sweep"]["num_timestep_levels"])
            num_freqs = 5 # i wrote a specific version of the code that actually carries 5 frequencies
            assert num_levels == 1
            entries = {
                "runtime[s]": runtime,
                "num_cores": int(num_cores),
                "resolution": "${}^3$".format(str(int(float(num_particles + 1) ** (1.0 / 3.0)))),
                "t_task[µs]": num_cores * runtime * 1e6 / num_particles / num_dirs / num_freqs,
            }
            dfs.append(pl.DataFrame(entries))
        df = pl.concat(dfs)
        one_core = df.bottom_k(1, by="num_cores")
        df = df.with_columns((one_core["t_task[µs]"] / pl.col("t_task[µs]")).alias("t_task_relative"))
        return pl.concat(extend(df) for (_, df) in df.groupby("resolution"))

    def plot(self, plt: plt.axes, df: Result) -> None:
        fig, axes = plt.subplots(2, 1, sharex=True)
        ax0, ax1 = axes
        sns.lineplot(y=df["t_task[µs]"], x=df["num_cores"], hue=df["resolution"], ax=ax0)
        sns.lineplot(y=df["t_task_relative"], x=df["num_cores"], hue=df["resolution"], ax=ax1)
        ax1.set(xlabel="$n$", xscale="log", xlim=self.config["xLim"])
        ax0.set(ylabel="$t_{\\text{task}}(n)$")
        ax1.set(ylabel="$t_{\\text{task}}(n) / t_{\\text{task}}(1)$", ylim=[0, 1])


class StrongScalingSpeedup(StrongScaling):
    def plot(self, plt: plt.axes, df: Result) -> None:
        fig, axes = plt.subplots(2, 1, sharex=True)
        ax0, ax1 = axes
        ax0.plot(np.arange(1, 200), np.arange(1, 200), label="ideal", color="black", linestyle="--")
        ax0.plot(np.arange(96, 1024), np.arange(96, 1024) / 96, label="ideal", color="red", linestyle="--")
        sns.lineplot(y=df["speedup"], x=df["num_cores"], hue=df["resolution"], ax=ax0)
        sns.lineplot(y=df["efficiency"], x=df["num_cores"], hue=df["resolution"], ax=ax1)
        ax1.set(xlabel="$n$", xscale="log", xlim=self.config["xLim"])
        ax0.set(ylabel="$S(n)$", ylim=[0, 100])
        ax1.set(ylabel="$\\epsilon(n)$", ylim=[0, 1])
