from typing import Iterable, List, Any, Tuple, Dict
import itertools
import os
from pathlib import Path
import argparse
from bob.simulation import Simulation
from bob.util import getNiceParamName


class SimulationSet(list):
    def __init__(self, sims: Iterable[Simulation]) -> None:
        super().__init__(sims)
        assert len(self) > 0, "Error: No sim found!"
        self.variedParams = set(k for k in self[0].params if self.doesVary(k))
        self.commonParams = self[0].params.keys() - self.variedParams

    def doesVary(self, k: str) -> bool:
        return len(set(sim.params.get(k) for sim in self)) > 1

    def quotient(self, parameters: List[str]) -> List[Tuple[Dict[str, Any], "SimulationSet"]]:
        def getConfiguration(sim: Simulation) -> Tuple[Tuple[Any, Any], ...]:
            return tuple((k, sim.params[k]) for k in parameters)

        configurations = list(set(getConfiguration(sim) for sim in self))
        configurations.sort()
        return [
            (
                dict(configuration),
                SimulationSet(
                    [sim for sim in self if getConfiguration(sim) == configuration],
                ),
            )
            for configuration in configurations
        ]

    def getNiceSimName(self, sim: Simulation) -> str:
        assert sim in self
        result = ",".join(getNiceParamName(k, sim.params[k]) for k in self.variedParams if getNiceParamName(k, sim.params[k]) != "")
        return result

    def getNiceSubsetName(self, params: Dict[str, Any], simSet: "SimulationSet") -> str:
        assert all(sim in self for sim in simSet)
        result = ",".join(getNiceParamName(k, simSet[0].params[k]) for k in params if getNiceParamName(k, simSet[0].params[k]) != "")
        return result


def isSimulationDirectory(folder: str) -> bool:
    # This is a bit ugly and needs to change to allow different simulation names. The check probably
    # needs to be removed and replaced by strictly adhering to a directory structure
    return stringIsInt(folder) and Path(folder).is_dir()


def getSimsFromFolder(sim_set_folder: Path) -> SimulationSet:
    folders = [sim_set_folder / Path(folder) for folder in os.listdir(sim_set_folder) if stringIsInt(folder)]
    folders.sort(key=lambda x: int(str(x.stem)))
    return SimulationSet((Simulation(folder) for folder in folders))


def joined(simSets: List[SimulationSet]) -> SimulationSet:
    return SimulationSet(itertools.chain(*simSets.__iter__()))


def getSimsFromFolders(args: argparse.Namespace) -> SimulationSet:
    sims = [getSimsFromFolder(folder) for folder in args.simFolders]
    return joined(sims)


def stringIsInt(s: str) -> bool:
    try:
        _ = int(s)
        return True
    except ValueError:
        return False
