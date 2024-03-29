import matplotlib.pyplot as plt
import astropy.units as pq
from bob.postprocessingFunctions import MultiSetFn
from bob.result import Result
from bob.multiSet import MultiSet
from bob.plots.timePlots import addTimeArg
from bob.util import getArrayQuantity

from bob.plotConfig import PlotConfig


class LuminosityOverTime(MultiSetFn):
    def __init__(self, config: PlotConfig) -> None:
        super().__init__(config)
        addTimeArg(self)
        self.config.setDefault("xLabel", "t")
        self.config.setDefault("yLabel", "L")
        self.config.setDefault("xUnit", "Gyr")
        self.config.setDefault("yUnit", "1 / s")

    def post(self, simSets: MultiSet) -> Result:
        result = Result()
        result.data = []
        for simSet in simSets:
            subresult = Result()
            subresult.time = getArrayQuantity([sim.snapshots[0].getTimeQuantity(self.config["time"]) for sim in simSet])
            sources = [sim.sources().sed for sim in simSet]
            subresult.luminosity = getArrayQuantity([sum(sum(s) for s in source) / pq.s for source in sources])
            result.data.append(subresult)
        return result

    def plot(self, plt: plt.axes, result: Result) -> None:
        for subresult in result.data:
            self.addLine(subresult.time, subresult.luminosity)
        plt.legend()
