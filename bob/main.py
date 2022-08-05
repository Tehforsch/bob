from typing import List
from pathlib import Path
import logging
import argparse

import bob.postprocess
from bob.simulationSet import getSimsFromFolders, SimulationSet
from bob.util import getCommonParentFolder
from bob.watch import watchPost, watchReplot
from bob.plotter import Plotter
from bob.postprocess import readPlotFile, setMatplotlibStyle


def commaSeparatedList(s: str) -> List[str]:
    return s.split(",")


def setupArgs() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Postprocess arepo sims")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--show", action="store_true", help="Show figures instead of saving them")

    subparsers = parser.add_subparsers(dest="function")
    plotParser = subparsers.add_parser("plot")
    plotParser.add_argument("simFolders", type=Path, nargs="+", help="Path to simulation directories")
    plotParser.add_argument("plot", type=Path, help="The plot configuration")
    parser.add_argument("--post", action="store_true", help="Only postprocess the data, do not run the corresponding plot scripts (for cluster)")

    replotParser = subparsers.add_parser("replot")
    replotParser.add_argument("simFolders", type=Path, nargs="+", help="Path to simulation directories")
    replotParser.add_argument("--plots", type=str, nargs="*", help="The plots to replot")
    replotParser.add_argument("--types", type=str, nargs="*", help="The plot types to replot")
    replotParser.add_argument(
        "--only-new",
        dest="onlyNew",
        action="store_true",
        help="Replot all plots that have new data or havent been generated yet but don't refresh old ones",
    )

    watchPostParser = subparsers.add_parser("watchPost")
    watchPostParser.add_argument("communicationFolder", type=Path, help="The folder to watch for new commands")
    watchPostParser.add_argument("workFolder", type=Path, help="The work folder to execute the commands in")

    watchReplotParser = subparsers.add_parser("watchReplot")
    watchReplotParser.add_argument("communicationFolder", type=Path, help="The folder to watch for new replot commands (.done files)")
    watchReplotParser.add_argument("remoteWorkFolder", type=Path, help="The folder from which the plots should be copied")
    watchReplotParser.add_argument("localWorkFolder", type=Path, help="The folder to which the plots should be copied and replotted")

    args = parser.parse_args()
    return args


def setupLogging(args: argparse.Namespace) -> None:
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)


def main() -> None:
    args = setupArgs()
    setupLogging(args)
    if args.function == "watchPost":
        watchPost(args.communicationFolder, args.workFolder)
    if args.function == "watchReplot":
        setMatplotlibStyle()
        watchReplot(args.communicationFolder, args.localWorkFolder, args.remoteWorkFolder)
    if not args.post:
        setMatplotlibStyle()
    if args.function == "replot":
        plotter = Plotter(Path("."), SimulationSet([]), args.post, args.show)
        plotter.replot(args.plots, args.onlyNew)
    else:
        sims = getSimsFromFolders(args.simFolders)
        parent_folder = getCommonParentFolder(args.simFolders)
        bob.postprocess.create_pic_folder(parent_folder)
        plotter = Plotter(parent_folder, sims, args.post, args.show)
        functions = readPlotFile(args.plot, True)
        bob.postprocess.runFunctionsWithPlotter(plotter, functions)
