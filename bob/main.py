from pathlib import Path
import shutil
import logging
import argparse


from bob import postprocess, config
from bob import postprocessingFunctions
from bob.simulationSet import getSimsFromFolder
from bob.units import setupUnits


def setupArgs() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Postprocess arepo sims")
    functionNames = postprocessingFunctions.functionNames()
    parser.add_argument("simFolder", type=Path, help="Sim folder")
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
    parser.add_argument(
        "functions",
        choices=functionNames,
        nargs="+",
        help="Which postprocessing functions to run",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument(
        "--show", action="store_true", help="Show figures instead of saving them"
    )
    parser.add_argument(
        "--recalc", action="store_true", help="Recalculate memoized results"
    )

    args = parser.parse_args()
    args.simFolder = args.simFolder.expanduser()
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
    sims = getSimsFromFolder(args)
    if args.recalc:
        shutil.rmtree(config.memoizeDir)
    postprocess.main(args, sims)
