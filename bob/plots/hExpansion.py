import matplotlib.pyplot as plt
import numpy as np
import astropy.units as pq

from bob.multiSet import MultiSet
from bob.postprocessingFunctions import MultiSetFn
from bob.result import Result
from bob.plotConfig import PlotConfig
from bob.fieldOverRadius import getDataForRadii
from bob.basicField import BasicField


class HExpansion(MultiSetFn):
    def __init__(self, config: PlotConfig) -> None:
        super().__init__(config)
        self.config.setDefault("num", 20)
        self.config.setDefault("xLabel", "r [UNIT]")
        self.config.setDefault("yLabel", "F [UNIT]")
        self.config.setDefault("xUnit", "kpc")
        self.config.setDefault("yUnit", "1")

    def post(self, simSets: MultiSet) -> Result:
        result = Result()
        result.data = []
        boxSize = simSets.sims[0][0].boxSize() / 2.0
        result.radii = np.linspace(0, boxSize, num=self.config["num"])
        for simSet in simSets:
            subresult = Result()
            snaps = [snap for sim in simSet for snap in [sim.snapshots[0], sim.snapshots[5], sim.snapshots[20], sim.snapshots[50]]]
            subresult.abundances = []
            for snap in snaps:
                coordinates = snap.coordinates
                center = np.array([1, 1, 1]) * boxSize
                abundances = BasicField("ChemicalAbundances").getData(snap)

                subresult.abundances.append(getDataForRadii(abundances[:], center, coordinates, result.radii))
            result.data.append(subresult)
        return result

    def plot(self, plt: plt.axes, result: Result) -> plt.Figure:
        fig, ax0 = plt.subplots(1, 1)
        self.setupLabels()
        labels = self.getLabels()
        colors = self.getColors()
        for label, color, subresult in zip(labels, colors, result.data):
            ax0.plot([], [], color=color, label=label)
            for ab in subresult.abundances:
                self.addLine(result.radii.to(pq.pc), ab, color=color, label="")
        plt.legend(loc="upper right")
        return fig
