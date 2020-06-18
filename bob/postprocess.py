import argparse
from typing import Callable, List, Any
from pathlib import Path
from bob.simulationSet import SimulationSet
from bob import config
import bob.scaling
import bob.gprof
import matplotlib.pyplot as plt
import bob.plot


def checkNoDoubledNames() -> None:
    assert len(set(functionNames)) == len(functionNames), "Two functions with the same name in postprocessing functions!"


def getSpecifiedFunctions(args: argparse.Namespace, functions: List[Callable[..., Any]]) -> List[Callable[..., Any]]:
    if args.functions is None:
        return functions
    else:
        return [function for function in functions if function.__name__ in args.functions]


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
    for function in getSpecifiedFunctions(args, postprocessFunctions):
        function(sims)
    for function in getSpecifiedFunctions(args, plotFunctions):
        bob.plot.runPlot(function, sims, args)


plotFunctions: List[Callable[[plt.axes, SimulationSet], None]] = [bob.scaling.speedup, bob.scaling.runTime]
postprocessFunctions: List[Callable[[SimulationSet], None]] = [bob.gprof.runGprof]
functionNames: List[str] = [f.__name__ for f in plotFunctions] + [f.__name__ for f in postprocessFunctions]
checkNoDoubledNames()
