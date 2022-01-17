from pathlib import Path
import shutil
import logging
import argparse

from bob import postprocess, config
from bob import postprocessingFunctions
from bob.simulationSet import getSimsFromFolders
from bob.units import setupUnits
from bob.util import getCommonParentFolder


def setupArgs() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Postprocess arepo sims")
    functionNames = postprocessingFunctions.functionNames()
    parser.add_argument("simFolders", type=Path, nargs="*", help="Path to simulation directories")
    parser.add_argument(
        "--snapshots",
        nargs="+",
        type=str,
        help="Run postprocessing scripts for selected snapshots",
    )
    parser.add_argument(
        "-s",
        "--select",
        nargs="*",
        help="Select only some of the sims for postprocessing/running/compiling",
    )
    parser.add_argument("-q", "--quotient", nargs="*", help="Parameters by which to divide the simulations into sets")
    parser.add_argument(
        "functions",
        choices=functionNames,
        nargs="+",
        help="Which postprocessing functions to run",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--show", action="store_true", help="Show figures instead of saving them")
    parser.add_argument("--recalc", action="store_true", help="Recalculate memoized results")

    args = parser.parse_args()
    return args


def setupLogging(args: argparse.Namespace) -> None:
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)


def main() -> None:
    args = setupArgs()
    setupUnits()
    setupLogging(args)
    sims = getSimsFromFolders(args)
    if args.recalc:
        shutil.rmtree(config.memoizeDir)
    folder = getCommonParentFolder(args.simFolders)
    postprocess.main(args, folder, sims)
