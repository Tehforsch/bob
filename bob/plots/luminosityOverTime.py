import argparse
import matplotlib.pyplot as plt
import astropy.units as pq
from bob.postprocessingFunctions import MultiSetFn
from bob.result import Result
from bob.multiSet import MultiSet
from bob.plots.timePlots import getTimeQuantityForSnap, addTimeArg
from bob.postprocessingFunctions import addToList
from bob.util import getArrayQuantity


class LuminosityOverTime(MultiSetFn):
    def post(self, args: argparse.Namespace, simSets: MultiSet) -> Result:
        result = Result()
        result.data = []
        for simSet in simSets:
            subresult = Result()
            subresult.time = getArrayQuantity([getTimeQuantityForSnap(args.time, sim, sim.snapshots[0]) for sim in simSet])
            sources = [sim.sources().sed for sim in simSet]
            subresult.luminosity = getArrayQuantity([sum(sum(s) for s in source) / pq.s for source in sources])
            result.data.append(subresult)
        return result

    def plot(self, plt: plt.axes, result: Result) -> None:
        self.config.setDefault("xLabel", "t")
        self.config.setDefault("yLabel", "L")
        self.config.setDefault("xUnit", "Gyr")
        self.config.setDefault("yUnit", "1 / s")
        for subresult in result.data:
            self.addLine(subresult.time, subresult.luminosity)
        plt.legend()

    def setArgs(self, subparser: argparse.ArgumentParser) -> None:
        super().setArgs(subparser)
        addTimeArg(subparser)


addToList("luminosityOverTime", LuminosityOverTime())
