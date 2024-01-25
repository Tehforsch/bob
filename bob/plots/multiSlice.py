from typing import Tuple
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from scipy.spatial import cKDTree
import numpy as np
import astropy.units as pq
import astropy.cosmology.units as cu

from bob.simulation import Simulation
from bob.subsweepSimulation import Cosmology
from bob.snapshot import Snapshot
from bob import config
from bob.multiSet import MultiSet
from bob.postprocessingFunctions import MultiSetFn, PostprocessingFunction
from bob.result import Result
from bob.allFields import allFields, getFieldByName
from bob.field import Field
from bob.plotConfig import PlotConfig
from bob.plots.bobSlice import Slice
from bob.basicField import BasicField


class MultiSlice(MultiSetFn):
    def __init__(self, config: PlotConfig) -> None:
        s = f"{config['field0']}_{config['field1']}_{config['field2']}"
        name = "multislice_" + s + "_{axis}"
        config["labels"] = None
        config.setDefault("quotient", "single")
        for i in range(3):
            config.setRequired("field" + str(i))
            config.setRequired("vLim" + str(i))
            config.setRequired("vUnit" + str(i))
            config.setRequired("cLabel" + str(i))
            config.setRequired("title_snap" + str(i))
        sl = Slice(config)
        self.config = sl.config
        self.config["name"] = name

    def iterConfigs(self):
        for i in range(3):
            config = self.config

            def s(name):
                config[name] = self.config[name + str(i)]

            s("vUnit")
            s("vLim")
            s("field")
            s("cLabel")
            s("title_snap")
            config["vUnit"] = self.config[f"vUnit{i}"]
            config["colorscale"] = None
            yield config

    def snapshots(self, simSets):
        for entry in self.config["snapshots"]:
            sim = next(sim[0] for sim in simSets if int(str(sim[0].folder)) == entry[0])
            yield (sim, sim.snapshots[entry[1]])

    def post(self, simSets: MultiSet) -> Result:
        result = Result()
        result.data = []
        for config in self.iterConfigs():
            for sim, snap in self.snapshots(simSets):
                result.data.append(Slice(config).post(sim, snap))
        return result

    def plot(self, plt: plt.axes, result: Result) -> plt.Figure:
        fig, axs = plt.subplots(3, 3, figsize=(11, 8), sharex=True, sharey=True, constrained_layout=True)
        for i, config in enumerate(self.iterConfigs()):
            for j in range(3):
                d = result.data[i * 3 + j]
                ax = axs[i][j]
                isRight = j == 2
                isLeft = j == 0
                isBottom = i == 2
                isTop = i == 0
                print(config["field"])
                Slice(config).plotData(ax, d, colorbar=isRight)
                self.setupLabels(ax, xlabel=isBottom, ylabel=isLeft)
                if isTop:
                    ax.annotate(
                        self.config[f"title_snap{j}"],
                        xy=(0.5, 0.9),
                        xytext=(0.45, 0.9),
                        xycoords="axes fraction",
                        textcoords="axes fraction",
                        fontsize=15,
                    )
