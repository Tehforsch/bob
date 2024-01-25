from typing import Iterable, List, Any, Tuple, Dict, Union
import itertools
import os
from pathlib import Path
from bob.simulation import Simulation
from bob.subsweepSimulation import SubsweepSimulation

AnySim = Simulation | SubsweepSimulation


class Single:
    pass


class SimulationSet(list):
    def __init__(self, sim_type: Any, sims: Iterable[AnySim]) -> None:
        super().__init__(sims)
        if len(self) == 1:
            self.label = self[0].label
        else:
            self.label = None
        self.sim_type = sim_type

    def quotient(self, parameters: Union[List[str], Single]) -> List[Tuple[Dict[str, Any], "SimulationSet"]]:
        def getConfiguration(sim: AnySim, parameters: List[str]) -> Tuple[Tuple[Any, Any], ...]:
            def getValue(k: str) -> Any:
                if k == "name":  # For cases where sim sets are indistuingishable by actual sim parameters
                    return sim.folder.parent
                if "/" in k:
                    split = k.split("/")
                    if len(split) != 2:
                        raise NotImplementedError("super easy to fix")
                    return sim.params[split[0]][split[1]]
                return sim.params[k]

            return tuple((k, getValue(k)) for k in parameters)

        if isinstance(parameters, Single):
            # Return one SimSet per simulation
            return [(dict(getConfiguration(sim, [])), SimulationSet(self.sim_type, [sim])) for sim in self]
        else:
            configurations = list(set(getConfiguration(sim, parameters) for sim in self))
            configurations.sort()
            return [
                (
                    dict(configuration),
                    SimulationSet(
                        self.sim_type,
                        [sim for sim in self if getConfiguration(sim, parameters) == configuration],
                    ),
                )
                for configuration in configurations
            ]


def getSims(folders, sim_type):
    for folder in folders:
        try:
            sim = sim_type(folder)
        except FileNotFoundError:
            print("skipping sim that probably didnt run:", folder)
            continue
        yield sim


def getSimsFromFolder(sim_type: Any, sim_set_folder: Path) -> SimulationSet:
    folders = [sim_set_folder / Path(folder) for folder in os.listdir(sim_set_folder) if stringIsInt(folder)]
    folders.sort(key=lambda x: int(str(x.stem)))
    return SimulationSet(sim_type, getSims(folders, sim_type))


def joined(simSets: List[SimulationSet]) -> SimulationSet:
    return SimulationSet(simSets[0].sim_type, itertools.chain(*simSets.__iter__()))


def getSimsFromFolders(sim_type: Any, simFolders: List[Path]) -> SimulationSet:
    sims = [getSimsFromFolder(sim_type, folder) for folder in simFolders]
    return joined(sims)


def stringIsInt(s: str) -> bool:
    try:
        _ = int(s)
        return True
    except ValueError:
        return False
