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
import bob.plot
import bob.plots.physicalPlots


from bob.postprocessingFunctions import (
    postprocessingFunctions,
    PostprocessingFunction,
    SnapFn,
    SetFn,
    MultiSetFn,
    SliceFn,
)


def getSpecifiedFunction(args: argparse.Namespace, functions: Sequence[PostprocessingFunction]) -> Sequence[PostprocessingFunction]:
    return next(function for function in functions if function.name == args.function)


def setMatplotlibStyle() -> None:
    file_path = Path(os.path.realpath(__file__))
    plt.style.use(Path(file_path).parent / "../styles/plot.mlpstyle")


def main(args: argparse.Namespace, parent_folder: Path, sims: SimulationSet) -> None:
    if not args.post:
        setMatplotlibStyle()

    picFolder = Path(parent_folder, config.picFolder)
    picFolder.mkdir(exist_ok=True)
    plotter = bob.plot.Plotter(parent_folder, sims, args.snapshots, args.show, args.select, args.quotient)
    function = getSpecifiedFunction(args, postprocessingFunctions)()
    if isinstance(function, SnapFn):
        plotter.runSnapFn(function)
    elif isinstance(function, SetFn):
        plotter.runSetFn(function)
    elif isinstance(function, MultiSetFn):
        plotter.runMultiSetFn(function)
    elif isinstance(function, SliceFn):
        plotter.runSliceFn(function)
    else:
        raise NotImplementedError
