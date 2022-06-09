from typing import Dict, Any
import argparse
import matplotlib.pyplot as plt
import astropy.units as pq
from bob.postprocessingFunctions import MultiSetFn
from bob.result import Result
from bob.multiSet import MultiSet
from bob.plots.timePlots import getTimeQuantityForSnap, addTimeArg
from bob.sources import Sources
from bob.postprocessingFunctions import addToList
from bob.util import getArrayQuantity


class LuminosityOverTime(MultiSetFn):
    def post(self, args: argparse.Namespace, simSets: MultiSet) -> Result:
        result = Result()
        result.data = []
        for simSet in simSets:
            subresult = Result()
            subresult.time = getArrayQuantity([getTimeQuantityForSnap(args.time, sim, sim.snapshots[0]) for sim in simSet])
            sources = [Sources(sim.folder / sim.params["TestSrcFile"]).sed for sim in simSet]
            subresult.luminosity = getArrayQuantity([sum(sum(s) for s in source) / pq.s for source in sources])
            result.data.append(subresult)
        return result

    def getStyleDefaults(self) -> Dict[str, Any]:
        return {
            "xLabel": "t",
            "yLabel": "L",
        }

    def plot(self, plt: plt.axes, result: Result) -> None:
        plt.xlabel(self.style["xLabel"])
        plt.ylabel(self.style["yLabel"])
        for subresult in result.data:
            plt.plot(subresult.time.to(pq.Gyr) / pq.Gyr, subresult.luminosity.to(1.0 / pq.s) * pq.s)
        plt.legend()

    def setArgs(self, subparser: argparse.ArgumentParser) -> None:
        super().setArgs(subparser)
        addTimeArg(subparser)


addToList("luminosityOverTime", LuminosityOverTime())
