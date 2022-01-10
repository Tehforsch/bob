import os
import argparse
from typing import Sequence
from pathlib import Path
from bob.simulationSet import SimulationSet
from bob import config
import bob.scaling
import matplotlib.pyplot as plt
import bob.plot
import bob.physicalPlots

from bob.postprocessingFunctions import (
    postprocessingFunctions,
    PostprocessingFunction,
    PlotFunction,
    SingleSimPlotFunction,
    SingleSnapshotPlotFunction,
    SingleSnapshotPostprocessingFunction,
)


def getSpecifiedFunctions(args: argparse.Namespace, functions: Sequence[PostprocessingFunction]) -> Sequence[PostprocessingFunction]:
    if args.functions is None:
        return functions
    else:
        return [function for function in functions if function.name in args.functions]


def setFontSizes() -> None:
    file_path = Path(os.path.realpath(__file__))
    plt.style.use(Path(file_path).parent / "../styles/plot.mlpstyle")


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
        elif isinstance(function, SingleSnapshotPostprocessingFunction):
            bob.plot.runSingleSnapshotPostprocessingFunction(function, sims, args)
        elif type(function) == PostprocessingFunction:
            function(sims)
