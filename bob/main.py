from typing import List, Dict, Any
from pathlib import Path
import logging
import argparse
import itertools
import math

import yaml

from bob import config
from bob.simulation import Simulation


def setupArgs() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compile and run arepo for changing parameters and config files.")
    parser.add_argument("inputFolder", type=Path, help="Folder containing the simulation input data.")
    parser.add_argument("outputFolder", type=Path, help="Folder into which the simulation is written.")
    parser.add_argument("-r", "--run", action="store_true", help="Run and compile the simulations after writing them")
    parser.add_argument("-c", "--create", action="store_true", help="Copy files and compile arepo if config file has changed")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

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


def getProductSubstitutions(subst: Dict[str, Any]) -> List[Dict[str, Any]]:
    params = list(subst.keys())
    configurations = itertools.product(*[subst[param] for param in params])
    return [dict((param, configuration[i]) for (i, param) in enumerate(params)) for configuration in configurations]


def getSimNames(dicts: List[Dict[str, Any]]) -> List[str]:
    # Pad integers as much as we need to.
    numSims = len(dicts)
    if numSims == 1:
        return ["0"]
    minPadding = int(math.log10(numSims - 1)) + 1
    names = [f"{i:0{minPadding}d}" for i in range(numSims)]
    return names


def createSimulations(args: argparse.Namespace) -> List[Simulation]:
    allSubstitutions = readSubstitutionsFile(args.inputFolder)
    if allSubstitutions == {}:
        return [Simulation(args.inputFolder, args.outputFolder, {})]
    if allSubstitutions.get(config.cartesianIdentifier, False):
        del allSubstitutions[config.cartesianIdentifier]
        dicts = getProductSubstitutions(allSubstitutions)
    else:
        numSims = len(next(iter(allSubstitutions.values())))
        for v in allSubstitutions.values():
            assert len(v) == numSims
        dicts = [dict((k, v[i]) for (k, v) in allSubstitutions.items()) for i in range(numSims)]
    names = getSimNames(dicts)
    return [Simulation(args.inputFolder, Path(args.outputFolder, name), d) for (name, d) in zip(names, dicts)]


def handleSimulations(args: argparse.Namespace, sims: List[Simulation]) -> None:
    for sim in sims:
        sim.compileArepo(args.verbose)
        if args.run:
            sim.run(args)


def main() -> None:
    args = setupArgs()
    setupLogging(args)
    if args.create:
        sims = createSimulations(args)
        handleSimulations(args, sims)
