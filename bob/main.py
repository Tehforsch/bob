from typing import List
from pathlib import Path
import logging
import argparse

from bob import postprocess
from bob import postprocessingFunctions
from bob.simulationSet import getSimsFromFolders, SimulationSet
from bob.util import getCommonParentFolder


def commaSeparatedList(s: str) -> List[str]:
    return s.split(",")


def setupArgs() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Postprocess arepo sims")
    parser.add_argument("simFolders", type=Path, nargs="*", help="Path to simulation directories")
    parser.add_argument(
        "--snapshots",
        type=commaSeparatedList,
        help="Run postprocessing scripts for selected snapshots",
    )
    parser.add_argument(
        "-s",
        "--select",
        type=commaSeparatedList,
        help="Select only some of the sims for postprocessing/running/compiling",
    )
    parser.add_argument("-q", "--quotient", nargs="*", help="Parameters by which to divide the simulations into sets")
    parser.add_argument("--single", action="store_true", help="Create simulation set for each simulation")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--show", action="store_true", help="Show figures instead of saving them")
    parser.add_argument("--post", action="store_true", help="Only postprocess the data, do not run the corresponding plot scripts (for cluster)")
    parser.add_argument("--png", action="store_true", help="Use png instead of pdf as output type for generating movies")
    parser.add_argument("--style", type=Path, help="Path to a style sheet to overwrite plot defaults with")
    subparsers = parser.add_subparsers(dest="function")
    for function in postprocessingFunctions.postprocessingFunctions:
        subparser = subparsers.add_parser(function.name)
        function.setArgs(subparser)
    replotParser = subparsers.add_parser("replot")
    replotParser.add_argument("--plots", type=str, nargs="*", help="The plots to replot")
    replotParser.add_argument("--types", type=str, nargs="*", help="The plot types to replot")
    replotParser.add_argument(
        "--only-new",
        dest="onlyNew",
        action="store_true",
        help="Replot all plots that have new data or havent been generated yet but don't refresh old ones",
    )

    args = parser.parse_args()
    return args


def setupLogging(args: argparse.Namespace) -> None:
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)


def main() -> None:
    args = setupArgs()
    if args.simFolders == []:
        raise ValueError("No sim folders given")
    setupLogging(args)
    if not args.function == "replot":
        sims = getSimsFromFolders(args)
    else:
        sims = SimulationSet([])
    folder = getCommonParentFolder(args.simFolders)
    postprocess.main(args, folder, sims)
