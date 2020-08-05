import shutil
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
        # for sim in self[1:]:
        # assert sim.params.keys() == self[0].params.keys(), "Not matching: {}".format(set(sim.params.keys()).difference(set(self[0].params.keys())))
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
        result = ",".join(getNiceParamName(k, sim.params[k]) for k in self.variedParams if getNiceParamName(k, sim.params[k]) != "")
        return result

    def getNiceSubsetName(self, params: List[str], simSet: "SimulationSet") -> str:
        assert all(sim in self for sim in simSet)
        result = ",".join(getNiceParamName(k, simSet[0].params[k]) for k in params if getNiceParamName(k, simSet[0].params[k]) != "")
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


def deleteFiles(folder: Path) -> None:
    if folder.is_dir():
        shutil.rmtree(folder)


def copyFiles(sourceFolder: Path, targetFolder: Path) -> None:
    shutil.copytree(sourceFolder, targetFolder)


def createSimulation(args: argparse.Namespace, name: str, d: Dict[str, Any]) -> Simulation:
    folder = Path(args.simFolder, name)
    if args.delete:
        deleteFiles(folder)
    if args.create:
        copyFiles(args.inputFolder, folder)
    return Simulation(folder, d)


def createSimsFromFolder(args: argparse.Namespace) -> SimulationSet:
    allSubstitutions = getAllSubstitutions(args)
    if allSubstitutions == {}:
        return SimulationSet(args.simFolder, [createSimulation(args, "sim", {})])
    if allSubstitutions.get(config.cartesianIdentifier, False):
        del allSubstitutions[config.cartesianIdentifier]
        dicts = getProductSubstitutions(allSubstitutions)
    else:
        numSims = len(next(iter(allSubstitutions.values())))
        for v in allSubstitutions.values():
            assert len(v) == numSims
        dicts = [dict((k, v[i]) for (k, v) in allSubstitutions.items()) for i in range(numSims)]
    names = getSimNames(dicts)
    return SimulationSet(args.simFolder, (createSimulation(args, name, d) for (name, d) in zip(names, dicts) if args.select is None or name in args.select))


def getSimsFromFolder(args: argparse.Namespace) -> SimulationSet:
    sims = createSimsFromFolder(args)
    for sim in sims:
        if args.create:
            sim.params.writeFiles()
    return sims
