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


def getFunctionByName(name: str, functions: Sequence[PostprocessingFunction]) -> Sequence[PostprocessingFunction]:
    return next(function for function in functions if function.name == name)


def setMatplotlibStyle() -> None:
    file_path = Path(os.path.realpath(__file__))
    plt.style.use(Path(file_path).parent / "../styles/plot.mlpstyle")


def main(args: argparse.Namespace, parent_folder: Path, sims: SimulationSet) -> None:
    if not args.post:
        setMatplotlibStyle()

    picFolder = Path(parent_folder, config.picFolder)
    picFolder.mkdir(exist_ok=True)
    plotter = bob.plot.Plotter(parent_folder, sims, args.snapshots, args.show, args.select, args.quotient)
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
