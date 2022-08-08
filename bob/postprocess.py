import os
from typing import List, Iterator, Union
from pathlib import Path
import yaml
import logging

try:
    import matplotlib.pyplot as plt
except ImportError:
    pass

from bob import config

from bob.plotter import Plotter

from bob.postprocessingFunctions import PostprocessingFunction
from bob.plotConfig import PlotConfig
from bob.plots.allFunctions import getFunctionByName

from bob.postprocessingFunctions import (
    SnapFn,
    SetFn,
    MultiSetFn,
    SliceFn,
)


def setMatplotlibStyle() -> None:
    file_path = Path(os.path.realpath(__file__))
    plt.style.use(Path(file_path).parent / "../styles/plot.mlpstyle")


def readPlotFile(filename: Path, safe: bool) -> dict:
    if safe:
        loader = yaml.SafeLoader
    else:
        loader = yaml.Loader
    return yaml.load(filename.open("r"), Loader=loader)


def getFunctionsFromPlotFile(filename: Path, safe: bool) -> List[PostprocessingFunction]:
    return getFunctionsFromPlotConfigs(readPlotFile(filename, safe))


def getFunctionsFromPlotConfigs(config: Union[dict, List[dict]]) -> List[PostprocessingFunction]:
    functions: List[PostprocessingFunction] = []
    if type(config) == dict:
        config = [config]
    for item in config:
        assert type(item) == dict
        assert len(item) == 1
        fnName = list(item.keys())[0]
        configItem = item[fnName]
        function = getFunctionByName(fnName)(PlotConfig(configItem))
        function.config.verify()
        functions.append(function)
    return functions


def runFunctionsWithPlotter(plotter: Plotter, functions: List[PostprocessingFunction]) -> Iterator[str]:
    logging.debug(functions)
    for function in functions:
        if isinstance(function, SnapFn):
            yield from plotter.runSnapFn(function)
        elif isinstance(function, SetFn):
            yield from plotter.runSetFn(function)
        elif isinstance(function, MultiSetFn):
            yield from plotter.runMultiSetFn(function)
        elif isinstance(function, SliceFn):
            yield from plotter.runSliceFn(function)
        else:
            raise NotImplementedError


def create_pic_folder(parent_folder: Path) -> None:
    picFolder = Path(parent_folder, config.picFolder)
    picFolder.mkdir(exist_ok=True)
