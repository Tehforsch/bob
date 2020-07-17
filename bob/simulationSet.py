from pathlib import Path
import itertools
from typing import List, Dict, Any, Iterable, Tuple, Set
import math
import argparse
import yaml
from bob import config
from bob.simulation import Simulation
from bob.util import getNiceParamName


class SimulationSet(list):
    def __init__(self, folder: Path, sims: Iterable[Simulation]) -> None:
        super().__init__(sims)
        self.folder = folder
        for sim in self[1:]:
            assert sim.params.keys() == self[0].params.keys()
        self.derivedParams = set.union(*(f.params.getDerivedParams() for f in self))
        self.variedParams = set(k for k in self[0].params if self.doesVary(k) and not k in self.derivedParams)
        self.commonParams = self[0].params.keys() - self.variedParams

    def doesVary(self, k: str) -> bool:
        return len(set(sim.params[k] for sim in self)) > 1

    def quotient(self, parameters: List[str]) -> List[Any]:
        remainingVariedParams = self.variedParams - set(parameters)
        getConfiguration = lambda sim: tuple((k, sim.params[k]) for k in remainingVariedParams)
        configurations = set(getConfiguration(sim) for sim in self)
        return [
            (dict(configuration), SimulationSet(self.folder, [sim for sim in self if getConfiguration(sim) == configuration]))
            for configuration in configurations
        ]

    def getNiceSimName(self, sim: Simulation) -> str:
        assert sim in self
        result = ",".join(getNiceParamName(k, sim.params[k]) for k in self.variedParams)
        return result


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


def getAllSubstitutions(args: argparse.Namespace) -> Dict[str, Any]:
    if args.create:
        return readSubstitutionsFile(args.inputFolder)
    else:
        simNames = list(f for f in args.simFolder.glob("*") if not f.name in config.specialFolders)
        assert len(simNames) > 0, "No simulation in output folder."
        return readSubstitutionsFile(Path(args.simFolder, simNames[0]))


def createSimsFromFolder(args: argparse.Namespace) -> SimulationSet:
    allSubstitutions = getAllSubstitutions(args)
    if allSubstitutions == {}:
        return SimulationSet(args.simFolder, [Simulation(args, "sim", {})])
    if allSubstitutions.get(config.cartesianIdentifier, False):
        del allSubstitutions[config.cartesianIdentifier]
        dicts = getProductSubstitutions(allSubstitutions)
    else:
        numSims = len(next(iter(allSubstitutions.values())))
        for v in allSubstitutions.values():
            assert len(v) == numSims
        dicts = [dict((k, v[i]) for (k, v) in allSubstitutions.items()) for i in range(numSims)]
    names = getSimNames(dicts)
    return SimulationSet(args.simFolder, (Simulation(args, name, d) for (name, d) in zip(names, dicts) if args.select is None or name in args.select))
