import os
import argparse
from typing import Sequence, List
from pathlib import Path
import yaml
import logging

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
import bob.plots.sliceWithStarParticles
from bob.postprocessingFunctions import PostprocessingFunction
from bob.plotConfig import PlotConfig


from bob.postprocessingFunctions import (
    postprocessingFunctions,
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


def readPlotFile(filename: Path) -> List[PostprocessingFunction]:
    config = yaml.load(filename.open("r"), Loader=yaml.SafeLoader)
    functions: List[PostprocessingFunction] = []
    for fnName in config:
        function = getFunctionByName(fnName, postprocessingFunctions)
        config = config[fnName]
        function.setArgs()
        function.setPlotConfig(PlotConfig(config))
        functions.append(function)
        print("still need to verify")
    return functions


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
        functions = readPlotFile(args.plot)
        logging.debug(functions)
        for function in functions:
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
