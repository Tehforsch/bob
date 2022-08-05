from typing import List
from pathlib import Path
import logging
import argparse

from bob import postprocess
from bob.simulationSet import getSimsFromFolders, SimulationSet
from bob.util import getCommonParentFolder
from bob.watch import watch


def commaSeparatedList(s: str) -> List[str]:
    return s.split(",")


def setupArgs() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Postprocess arepo sims")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--show", action="store_true", help="Show figures instead of saving them")
    parser.add_argument("--png", action="store_true", help="Use png instead of pdf as output type for generating movies")

    subparsers = parser.add_subparsers(dest="function")
    plotParser = subparsers.add_parser("plot")
    plotParser.add_argument("simFolders", type=Path, nargs="+", help="Path to simulation directories")
    plotParser.add_argument("plot", type=Path, help="The plot configuration")
    plotParser.add_argument("-q", "--quotient", nargs="*", help="Parameters by which to divide the simulations into sets")
    plotParser.add_argument("--single", action="store_true", help="Create simulation set for each simulation")
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

    replotParser = subparsers.add_parser("watch")
    replotParser.add_argument("communicationFolder", type=Path, help="The folder to watch for new commands")
    replotParser.add_argument("workFolder", type=Path, help="The work folder to execute the commands in")
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
    if args.function == "watch":
        watch(args, args.communicationFolder, args.workFolder)
        return
    if args.function == "replot":
        sims = SimulationSet([])
    else:
        sims = getSimsFromFolders(args.simFolders)
    folder = getCommonParentFolder(args.simFolders)
    postprocess.main(args, folder, sims)
