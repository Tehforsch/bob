from pathlib import Path
import logging
import argparse


from bob import postprocess
from bob.simulationSet import SimulationSet, fromFolder


def setupArgs() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compile and run arepo for changing parameters and config files.")
    postprocessingFunctions = [f.__name__ for f in postprocess.functions]
    parser.add_argument("inputFolder", type=Path, help="Folder containing the simulation input data.")
    parser.add_argument("outputFolder", type=Path, help="Folder into which the simulation is written.")
    parser.add_argument("-c", "--create", action="store_true", help="Copy files and compile arepo if config file has changed")
    parser.add_argument("-r", "--run", action="store_true", help="Run and compile the simulations after writing them")
    parser.add_argument("-p", "--postprocess", action="store_true", help="Run postprocessing scripts on an already run simulation")
    parser.add_argument("--functions", choices=postprocessingFunctions, help="Which postprocessing functions to run")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()
    args.inputFolder = args.inputFolder.expanduser()
    args.outputFolder = args.outputFolder.expanduser()
    return args


def setupLogging(args: argparse.Namespace) -> None:
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)


def runSimulations(args: argparse.Namespace, sims: SimulationSet) -> None:
    for sim in sims:
        sim.compileArepo(args.verbose)
        if args.run:
            sim.run(args)


def main() -> None:
    args = setupArgs()
    setupLogging(args)
    sims = fromFolder(args.create, args)
    if args.create:
        runSimulations(args, sims)
    if args.postprocess:
        postprocess.main(args, sims)
