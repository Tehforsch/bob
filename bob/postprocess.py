import os
import argparse
from typing import Sequence
from pathlib import Path

try:
    import matplotlib.pyplot as plt
except ImportError:
    pass

from bob.simulationSet import SimulationSet
from bob import config
import bob.plotter

import bob.plots.ionization
import bob.plots.ionizationRate
import bob.plots.ionizationTime
import bob.plots.timePlots
import bob.plots.thomsonScattering
import bob.plots.arepoSlice
import bob.plots.bobSlice
import bob.plots.shadowingVolume
import bob.plots.temperatureDensityHistogram
import bob.plots.temperatureIonizationHistogram
import bob.plots.temperatureOverTime
import bob.plots.meanFieldOverTime
import bob.plots.luminosityOverTime
import bob.plots.sourcePosition


from bob.postprocessingFunctions import (
    postprocessingFunctions,
    PostprocessingFunction,
    SnapFn,
    SetFn,
    MultiSetFn,
    SliceFn,
)


def getFunctionByName(name: str, functions: Sequence[PostprocessingFunction]) -> PostprocessingFunction:
    return next(function for function in functions if function.name == name)


def setMatplotlibStyle() -> None:
    file_path = Path(os.path.realpath(__file__))
    plt.style.use(Path(file_path).parent / "../styles/plot.mlpstyle")


def main(args: argparse.Namespace, parent_folder: Path, sims: SimulationSet) -> None:
    if not args.post:
        setMatplotlibStyle()

    picFolder = Path(parent_folder, config.picFolder)
    picFolder.mkdir(exist_ok=True)
    outputFileType = ".png" if args.png else ".pdf"
    plotter = bob.plotter.Plotter(parent_folder, sims, args.snapshots, args.show, args.select, args.quotient, args.single, outputFileType)
    if args.function == "replot":
        plotter.replot(args)
    else:
        function = getFunctionByName(args.function, postprocessingFunctions)
        if isinstance(function, SnapFn):
            plotter.runSnapFn(args, function)
        elif isinstance(function, SetFn):
            plotter.runSetFn(args, function)
        elif isinstance(function, MultiSetFn):
            plotter.runMultiSetFn(args, function)
        elif isinstance(function, SliceFn):
            plotter.runSliceFn(args, function)
        else:
            raise NotImplementedError
