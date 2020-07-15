import argparse
from typing import Sequence
from pathlib import Path
from bob.simulationSet import SimulationSet
from bob import config
import bob.scaling
import bob.gprof
import matplotlib.pyplot as plt
import bob.plot
import bob.physicalPlots
import bob.compareSimulations
from bob.postprocessingFunctions import postprocessingFunctions, PostprocessingFunction, PlotFunction, SingleSimPlotFunction, SingleSnapshotPlotFunction


def getSpecifiedFunctions(args: argparse.Namespace, functions: Sequence[PostprocessingFunction]) -> Sequence[PostprocessingFunction]:
    if args.functions is None:
        return functions
    else:
        return [function for function in functions if function.name in args.functions]


def setFontSizes() -> None:
    plt.rcParams["axes.labelsize"] = config.fontSize
    plt.rcParams["axes.titlesize"] = config.fontSize
    plt.rcParams["legend.fontsize"] = config.fontSize
    plt.rcParams["xtick.labelsize"] = config.fontSize
    plt.rcParams["ytick.labelsize"] = config.fontSize


def main(args: argparse.Namespace, sims: SimulationSet) -> None:
    setFontSizes()
    picFolder = Path(args.simFolder, config.picFolder)
    picFolder.mkdir(exist_ok=True)
    for function in getSpecifiedFunctions(args, postprocessingFunctions):
        if isinstance(function, PlotFunction):
            bob.plot.runPlot(function, sims, args)
        elif isinstance(function, SingleSimPlotFunction):
            bob.plot.runSingleSimPlot(function, sims, args)
        elif isinstance(function, SingleSnapshotPlotFunction):
            bob.plot.runSingleSnapshotPlot(function, sims, args)
        elif type(function) == PostprocessingFunction:
            function(sims)
