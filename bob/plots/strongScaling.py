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


def getOldResults(runtime, num_cores, resolution):
    num_particles = 9999999991
    num_dirs = 84
    num_freqs = 5
    df = pl.DataFrame(
        {
            "runtime[s]": runtime,
            "num_cores": num_cores,
            "resolution": [resolution for _ in runtime],
            "num_particles": num_particles,
            "t_task[µs]": [num_cores[i] * runtime[i] * 1e6 / num_particles / num_dirs / num_freqs for i in range(len(runtime))],
        }
    )
    one_core = df.bottom_k(1, by="num_cores")
    df = df.with_columns((one_core["t_task[µs]"] / pl.col("t_task[µs]")).alias("t_task_relative"))
    return pl.concat(extend(df) for (_, df) in df.groupby("resolution"))


def getOld32():
    num_cores = [1, 2, 4]
    runtime = [1.0, 2.0, 3.0]
    return getOldResults(runtime, num_cores, "$32^3$ (Arepo)")


def getOld256():
    num_cores = [1, 2, 4]
    runtime = [1.0, 2.0, 3.0]
    return getOldResults(runtime, num_cores, "$256^3$ (Arepo)")


def getOld512():
    num_cores = [1, 2, 4]
    runtime = [1.0, 2.0, 3.0]
    return getOldResults(runtime, num_cores, "$512^3$ (Arepo)")


def removeLegendTitle(ax):
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles=handles[0:], labels=labels[0:])


def removeLegend(ax):
    ax.legend().remove()


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
            assert perf["Stages::Sweep"]["num_calls"] == 32
            num_cores = int(perf["num_ranks"])
            num_particles = int(perf["num_particles"])
            num_dirs = int(sim.params["sweep"]["directions"])
            num_levels = int(sim.params["sweep"]["num_timestep_levels"])
            num_freqs = 5  # i wrote a specific version of the code that actually carries 5 frequencies
            assert num_levels == 1
            entries = {
                "runtime[s]": runtime,
                "num_cores": int(num_cores),
                "resolution": "${}^3$".format(str(int(float(num_particles + 1) ** (1.0 / 3.0)))),
                "num_particles": num_particles,
                "t_task[µs]": num_cores * runtime * 1e6 / num_particles / num_dirs / num_freqs,
            }
            dfs.append(pl.DataFrame(entries))
        df = pl.concat(dfs)
        one_core = df.bottom_k(1, by="num_cores")
        df = df.with_columns((one_core["t_task[µs]"] / pl.col("t_task[µs]")).alias("t_task_relative"))
        return pl.concat(extend(df) for (_, df) in df.groupby("resolution"))

    def plot(self, plt: plt.axes, df: Result) -> None:
        print(df)
        df = pl.concat([df, getOld32(), getOld256(), getOld512()])
        df = df.sort(by="num_particles")
        fig, axes = plt.subplots(2, 1, sharex=True)
        ax0, ax1 = axes
        sns.lineplot(y=df["t_task[µs]"], x=df["num_cores"], hue=df["resolution"], ax=ax0)
        sns.lineplot(y=df["t_task_relative"], x=df["num_cores"], hue=df["resolution"], ax=ax1)
        ax0.set_yscale("log")
        ax0.set_yticks([1e-1, 1e0, 1e1])
        ax0.set_ylim([1e-1, 1e1])
        ax1.set(xlabel="$n$", xscale="log", xlim=self.config["xLim"])
        ax0.set(ylabel="$t_{\\text{task}}(n) [\\mu s]$")
        ax1.set(ylabel="$t_{\\text{task}}(1) / t_{\\text{task}}(n)$", ylim=[0, 1])
        removeLegendTitle(ax0)
        removeLegend(ax1)


class StrongScalingSpeedup(StrongScaling):
    def plot(self, plt: plt.axes, df: Result) -> None:
        df = df.sort(by="num_particles")
        fig, axes = plt.subplots(2, 1, sharex=True)
        ax0, ax1 = axes
        ax0.plot([], [], label="ideal", color="black", linestyle="--")
        ax0.plot(np.arange(1, 200), np.arange(1, 200), color="#1f77b4", linestyle="--")
        ax0.plot(np.arange(8, 1024), np.arange(8, 1024) / 8, color="red", linestyle="--")
        ax0.plot(np.arange(64, 2048), np.arange(64, 2048) / 64, color="green", linestyle="--")
        ax0.plot(np.arange(512, 2048), np.arange(512, 2048) / 512, color="purple", linestyle="--")
        sns.lineplot(y=df["speedup"], x=df["num_cores"], hue=df["resolution"], ax=ax0)
        sns.lineplot(y=df["efficiency"], x=df["num_cores"], hue=df["resolution"], ax=ax1)
        ax1.set(xlabel="$n$", xscale="log", xlim=self.config["xLim"])
        ax0.set(ylabel="$S(n)$", ylim=[0, 100])
        ax1.set(ylabel="$\\epsilon(n)$", ylim=[0, 1])
        ax0.set_ylim([0, 50])
        removeLegendTitle(ax0)
        removeLegend(ax1)
