import os
import argparse
from typing import Sequence, List, Type
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


def getFunctionByName(name: str, functions: Sequence[Type[PostprocessingFunction]]) -> Type[PostprocessingFunction]:
    return next(function for function in functions if function.name == name)


def setMatplotlibStyle() -> None:
    file_path = Path(os.path.realpath(__file__))
    plt.style.use(Path(file_path).parent / "../styles/plot.mlpstyle")


def readPlotFile(filename: Path, safe: bool) -> List[PostprocessingFunction]:
    if safe:
        loader = yaml.SafeLoader
    else:
        loader = yaml.Loader
    config = yaml.load(filename.open("r"), Loader=loader)
    functions: List[PostprocessingFunction] = []
    for fnName in config:
        config = config[fnName]
        function = getFunctionByName(fnName, postprocessingFunctions)(PlotConfig(config))
        function.config.verify()
        functions.append(function)
    return functions


def main(args: argparse.Namespace, parent_folder: Path, sims: SimulationSet) -> None:
    if not args.post:
        setMatplotlibStyle()

    picFolder = Path(parent_folder, config.picFolder)
    picFolder.mkdir(exist_ok=True)
    if args.function == "replot":
        plotter = bob.plotter.Plotter(parent_folder, sims, args.show)
        plotter.replot(args)
    else:
        plotter = bob.plotter.Plotter(parent_folder, sims, args.show)
        functions = readPlotFile(args.plot, True)
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
