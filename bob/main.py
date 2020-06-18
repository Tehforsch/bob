from pathlib import Path
import logging
import argparse


from bob import postprocess
from bob.simulationSet import SimulationSet, createSimsFromFolder


def setupArgs() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compile and run arepo for changing parameters and config files.")
    postprocessingFunctions = postprocess.functionNames
    parser.add_argument("simFolder", type=Path, help="Folder into which the simulation is written.")
    parser.add_argument("-c", "--create", nargs=1, help="Read the input directory and create simulations from it.")
    # parser.add_argument("inputFolder", type=Path, help="Folder containing the simulation input data.")
    parser.add_argument("-m", "--make", action="store_true", help="Compile arepo if config file changed and copy executable")
    parser.add_argument("-r", "--run", action="store_true", help="Run and compile the simulations after writing them")
    parser.add_argument("-p", "--postprocess", action="store_true", help="Run postprocessing scripts on an already run simulation")
    parser.add_argument("-d", "--delete", action="store_true", help="Delete old simulations if they exist")
    parser.add_argument("--functions", choices=postprocessingFunctions, help="Which postprocessing functions to run")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress compilation output")
    parser.add_argument("-s", "--showFigures", action="store_true", help="Show figures instead of saving them")

    args = parser.parse_args()
    if args.create is not None:
        args.inputFolder = Path(args.create[0])
        args.inputFolder = args.inputFolder.expanduser()
    args.simFolder = args.simFolder.expanduser()
    return args


def setupLogging(args: argparse.Namespace) -> None:
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)


def makeSimulations(args: argparse.Namespace, sims: SimulationSet) -> None:
    for sim in sims:
        sim.compileArepo(args.quiet)


def runSimulations(args: argparse.Namespace, sims: SimulationSet) -> None:
    for sim in sims:
        sim.run(args)


def main() -> None:
    args = setupArgs()
    setupLogging(args)
    sims = createSimsFromFolder(args)
    if args.make:
        makeSimulations(args, sims)
    if args.run:
        runSimulations(args, sims)
    if args.postprocess:
        postprocess.main(args, sims)
