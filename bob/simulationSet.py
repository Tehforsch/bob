import shutil
from pathlib import Path
import itertools
from typing import List, Dict, Any, Iterable, Tuple, Set, Union
import math
import argparse
import yaml
from bob import config
from bob.simulation import Simulation
from bob.util import getNiceParamName, toList
from bob.config import outputFolderIdentifier, initialSnapIdentifier, snapshotFileBaseIdentifier


class SimulationSet(list):
    def __init__(self, folder: Path, sims: Iterable[Simulation]) -> None:
        super().__init__(sims)
        self.folder = folder
        assert len(self) > 0, "Error: No sim found!"
        self.derivedParams = set.union(*(f.params.getDerivedParams() for f in self))
        self.variedParams = set(k for k in self[0].params if self.doesVary(k) and not k in self.derivedParams)
        self.commonParams = self[0].params.keys() - self.variedParams

    def doesVary(self, k: str) -> bool:
        return len(set(sim.params[k] for sim in self)) > 1

    def quotient(self, parameters: List[str]) -> List[Any]:
        remainingVariedParams = self.variedParams - set(parameters)
        getConfiguration = lambda sim: tuple((k, sim.params[k]) for k in remainingVariedParams)
        configurations = set(getConfiguration(sim) for sim in self)
        print(configurations)
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
    if not substitutionFile.is_file():
        return {}
    with open(substitutionFile, "r") as f:
        return yaml.load(f, yaml.SafeLoader)


@toList
def getProductSubstitutions(subst: Dict[Any, Any], cartesianOptions: Union[bool, List[List[str]]]) -> Iterable[Dict[str, Any]]:
    params = list(subst.keys())
    if isinstance(cartesianOptions, List):
        for combinedParams in cartesianOptions:
            assert all(
                param in params for param in combinedParams
            ), "Error in sims file: Parameter listed in cartesian product that is not given actual values."
            values = [subst[param] for param in combinedParams]
            assert (len(v) == len(values[0]) for v in values), "Unequal parameter list lengths for params: {}".format(cartesianOptions)
            for param in combinedParams:
                del subst[param]
            subst[tuple(combinedParams)] = list(zip(*values))
    params = list(subst.keys())
    configurations = itertools.product(*[subst[param] for param in params])
    for configuration in configurations:
        d = {}
        for (i, param) in enumerate(params):
            if type(param) == tuple:  # grouped params = varied at once
                assert type(configuration[i]) == tuple
                for (k, v) in zip(param, configuration[i]):
                    d[k] = v
            else:
                d[param] = configuration[i]
        yield d


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
        simNames = list(f for f in args.simFolder.glob("*") if (not f.name in config.specialFolders) and f.is_dir())
        assert len(simNames) > 0, "No simulation in output folder."
        return readSubstitutionsFile(Path(args.simFolder, simNames[0]))


def deleteFiles(folder: Path) -> None:
    if folder.is_dir():
        shutil.rmtree(folder)


def copyFiles(sourceFolder: Path, targetFolder: Path) -> None:
    shutil.copytree(sourceFolder, targetFolder)


def copyInitialSnapshot(folder: Path, sim: Simulation) -> None:
    outputFolderName = sim.params[outputFolderIdentifier]
    initialSnapshot = sim.params[initialSnapIdentifier]
    snapFileBase = sim.params[snapshotFileBaseIdentifier]
    outputFolder = Path(folder, outputFolderName)
    outputFolder.mkdir(exist_ok=True)
    nameFirstSnapshot = f"{snapFileBase}_000.hdf5"
    shutil.copyfile(Path(folder, initialSnapshot), Path(outputFolder, nameFirstSnapshot))


def createSimulation(args: argparse.Namespace, name: str, d: Dict[str, Any]) -> Simulation:
    folder = Path(args.simFolder, name)
    if args.delete:
        deleteFiles(folder)
    if args.create:
        copyFiles(args.inputFolder, folder)
    sim = Simulation(folder, d)
    if initialSnapIdentifier in sim.params:
        copyInitialSnapshot(folder, sim)
    return sim


def createSimsFromFolder(args: argparse.Namespace) -> SimulationSet:
    allSubstitutions = getAllSubstitutions(args)
    if allSubstitutions == {}:
        return SimulationSet(args.simFolder, [createSimulation(args, "0", {})])
    cartesianOptions = allSubstitutions.get(config.cartesianIdentifier, False)
    if cartesianOptions:
        del allSubstitutions[config.cartesianIdentifier]
        dicts = getProductSubstitutions(allSubstitutions, cartesianOptions)
    else:
        numSims = len(next(iter(allSubstitutions.values())))
        for v in allSubstitutions.values():
            assert len(v) == numSims
        dicts = [dict((k, v[i]) for (k, v) in allSubstitutions.items()) for i in range(numSims)]
    names = getSimNames(dicts)
    sims = SimulationSet(args.simFolder, (createSimulation(args, name, d) for (name, d) in zip(names, dicts) if args.select is None or name in args.select))
    return sims


def getSimsFromFolder(args: argparse.Namespace) -> SimulationSet:
    sims = createSimsFromFolder(args)
    for sim in sims:
        if args.create:
            sim.params.writeFiles()
    return sims
