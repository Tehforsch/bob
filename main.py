from typing import List, Dict, Any
from pathlib import Path
import logging
import argparse
import yaml

import config
from simulation import Simulation
import localConfig


def setupArgs() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compile and run arepo for changing parameters and config files.")
    parser.add_argument("inputFolder", type=Path, help="Folder containing the simulation input data.")
    parser.add_argument("outputFolder", type=Path, help="Folder into which the simulation is written.")
    parser.add_argument("-r", "--run", action="store_true", help="Run and compile the simulations after writing them")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    # parser.add_argument("--register", default=None, nargs="*", help="Show individual transactions of the accounts matching the query (default: all accounts)")
    # parser.add_argument("--budget", type=Path, help="Read the budget file and compare accounts to it")
    # parser.add_argument("--read", default=None, nargs="+", type=Path, help="Read the specified csv files and add them to the journal")
    # parser.add_argument("--empty", default=False, action="store_true", help="Print empty accounts?")
    # parser.add_argument("--start", default=None, type=util.dateFromIsoformat, help="Start date")
    # parser.add_argument("--end", default=None, type=util.dateFromIsoformat, help="End date")
    # parser.add_argument(
    #     "--period", default=Period(config.infinite), type=Period, help="Smallest period for which to aggregate entries in the register/budget commands"
    # )
    # parser.add_argument("--cash", default=False, action="store_true", help="Add a cash transaction")
    # parser.add_argument("--plot", default=None, nargs="+", type=str, choices=list(plots.plots.keys()) + ["all"], help="Show a plot showing the data.")
    # parser.add_argument(
    #     "--exact", default=False, action="store_true", help="Only accept exact pattern matches when specifying accounts (instead of any regex match)"
    # )
    # parser.add_argument(
    #     "--sum", default=False, action="store_true", help="Calculate the sum of the values of all the matching accounts for register/balance queries"
    # )
    # parser.add_argument("--average", default=False, action="store_true", help="Show the average change per period of the account.")
    # parser.add_argument("--invert", default=None, nargs="*", help="When calculating totals invert the passed accounts")

    args = parser.parse_args()
    return args


def setupLogging(args: argparse.Namespace) -> None:
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)


def readSubstitutionsFile(inputFolder: Path) -> Dict[str, Any]:
    substitutionFile = Path(inputFolder, config.substitutionFileName)
    with open(substitutionFile, "r") as f:
        return yaml.load(f, yaml.SafeLoader)


def createSimulations(args: argparse.Namespace) -> List[Simulation]:
    allSubstitutions = readSubstitutionsFile(args.inputFolder)
    if allSubstitutions == {}:
        return [Simulation(args.inputFolder, args.outputFolder, {})]
    numSims = len(next(iter(allSubstitutions.values())))
    for v in allSubstitutions.values():
        assert len(v) == numSims

    return [Simulation(args.inputFolder, Path(args.outputFolder, str(i)), dict((k, v[i]) for (k, v) in allSubstitutions.items())) for i in range(numSims)]


def runSimulations(args: argparse.Namespace, sims: List[Simulation]) -> None:
    for sim in sims:
        sim.compileArepo(args.verbose)
        sim.run(args)


def main() -> None:
    args = setupArgs()
    setupLogging(args)
    sims = createSimulations(args)
    if args.run:
        runSimulations(args, sims)


# runOutputSimulations(sims)


if __name__ == "__main__":
    main()
