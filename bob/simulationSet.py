from typing import Iterable, List, Any, Tuple, Dict, Union
import itertools
import os
from pathlib import Path
from bob.simulation import Simulation


class Single:
    pass


class SimulationSet(list):
    def __init__(self, sims: Iterable[Simulation]) -> None:
        super().__init__(sims)

    def quotient(self, parameters: Union[List[str], Single]) -> List[Tuple[Dict[str, Any], "SimulationSet"]]:
        def getConfiguration(sim: Simulation, parameters: List[str]) -> Tuple[Tuple[Any, Any], ...]:
            def getValue(k: str) -> Any:
                if k == "name":  # For cases where sim sets are indistuingishable by actual sim parameters
                    return sim.folder.parent
                return sim.params[k]

            return tuple((k, getValue(k)) for k in parameters)

        if isinstance(parameters, Single):
            # Return one SimSet per simulation
            return [(dict(getConfiguration(sim, [])), SimulationSet([sim])) for sim in self]
        else:
            configurations = list(set(getConfiguration(sim, parameters) for sim in self))
            configurations.sort()
            return [
                (
                    dict(configuration),
                    SimulationSet(
                        [sim for sim in self if getConfiguration(sim, parameters) == configuration],
                    ),
                )
                for configuration in configurations
            ]


def getSimsFromFolder(sim_set_folder: Path) -> SimulationSet:
    folders = [sim_set_folder / Path(folder) for folder in os.listdir(sim_set_folder) if stringIsInt(folder)]
    folders.sort(key=lambda x: int(str(x.stem)))
    return SimulationSet((Simulation(folder) for folder in folders))


def joined(simSets: List[SimulationSet]) -> SimulationSet:
    return SimulationSet(itertools.chain(*simSets.__iter__()))


def getSimsFromFolders(simFolders: List[Path]) -> SimulationSet:
    sims = [getSimsFromFolder(folder) for folder in simFolders]
    return joined(sims)


def stringIsInt(s: str) -> bool:
    try:
        _ = int(s)
        return True
    except ValueError:
        return False
