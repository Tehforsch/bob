from typing import Iterable, List, Any, Tuple
import os
from pathlib import Path
import argparse
from bob.simulation import Simulation
from bob.util import getNiceParamName


class SimulationSet(list):
    def __init__(self, folder: Path, sims: Iterable[Simulation]) -> None:
        super().__init__(sims)
        self.folder = folder
        assert len(self) > 0, "Error: No sim found!"
        self.derivedParams = set.union(*(f.params.getDerivedParams() for f in self))
        self.variedParams = set(k for k in self[0].params if self.doesVary(k) and k not in self.derivedParams)
        self.commonParams = self[0].params.keys() - self.variedParams

    def doesVary(self, k: str) -> bool:
        return len(set(sim.params[k] for sim in self)) > 1

    def quotient(self, parameters: List[str]) -> List[Any]:
        remainingVariedParams = self.variedParams - set(parameters)

        def getConfiguration(sim: Simulation) -> Iterable[Tuple[str, Any]]:
            return ((k, sim.params[k]) for k in remainingVariedParams)

        configurations = set(getConfiguration(sim) for sim in self)
        return [
            (
                dict(configuration),
                SimulationSet(
                    self.folder,
                    [sim for sim in self if getConfiguration(sim) == configuration],
                ),
            )
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


def getSimsFromFolder(args: argparse.Namespace) -> SimulationSet:
    folders = [folder for folder in os.listdir(args.simFolder) if stringIsInt(folder) and Path(folder)]
    folders.sort(key=lambda x: int(x))
    folders = [Path(folder) for folder in folders]
    return SimulationSet(args.simFolder, (Simulation(folder) for folder in folders))


def stringIsInt(s: str) -> bool:
    print(s)
    try:
        _ = int(s)
        return True
    except ValueError:
        return False
