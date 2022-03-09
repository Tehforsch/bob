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
import bob.image

from bob.postprocessingFunctions import (
    postprocessingFunctions,
    PostprocessingFunction,
    PlotFunction,
    MultiPlotFunction,
    SingleSimPlotFunction,
    SingleSnapshotPlotFunction,
    SingleSnapshotPostprocessingFunction,
    SlicePlotFunction,
)


def getSpecifiedFunctions(args: argparse.Namespace, functions: Sequence[PostprocessingFunction]) -> Sequence[PostprocessingFunction]:
    if args.functions is None:
        return functions
    else:
        return [function for function in functions if function.name in args.functions]


def setFontSizes() -> None:
    file_path = Path(os.path.realpath(__file__))
    plt.style.use(Path(file_path).parent / "../styles/plot.mlpstyle")


def main(args: argparse.Namespace, parent_folder: Path, sims: SimulationSet) -> None:
    setFontSizes()

    picFolder = Path(parent_folder, config.picFolder)
    picFolder.mkdir(exist_ok=True)
    plotter = bob.plot.Plotter(parent_folder, sims, args.snapshots, args.show, args.quotient)
    for function in getSpecifiedFunctions(args, postprocessingFunctions):
        if isinstance(function, PlotFunction):
            plotter.runPlot(function)
        elif isinstance(function, MultiPlotFunction):
            plotter.runMultiPlot(function)
        elif isinstance(function, SingleSimPlotFunction):
            plotter.runSingleSimPlot(function)
        elif isinstance(function, SingleSnapshotPlotFunction):
            plotter.runSingleSnapshotPlot(function)
        elif isinstance(function, SingleSnapshotPostprocessingFunction):
            plotter.runSingleSnapshotPostprocessingFunction(function)
        elif isinstance(function, SlicePlotFunction):
            plotter.runSlicePlotFunction(function)
        else:
            raise NotImplementedError
