import logging

from typing import Optional, List, Tuple, Any, Dict, Iterator

from bob.simulationSet import SimulationSet


class MultiSet:
    def __init__(self, simSets: List[Tuple[Dict[str, Any], SimulationSet]], labels: Optional[List[str]]) -> None:
        self.configs = [s[0] for s in simSets]
        self.sims = [s[1] for s in simSets]
        if labels is None:
            self.labels = [sim.label if sim.label is not None else str(i) for (i, sim) in enumerate(self.sims)]
        else:
            assert len(labels) == len(self.sims), f"Found {len(labels)} labels but {len(self.sims)} sims"
            self.labels = labels
        print("Simulation sets:")
        for (simSet, label, config) in zip(self.sims, self.labels, self.configs):
            logging.info(f"{simSet}, {label}, {config}")

    def iterWithConfigs(self) -> Iterator[Tuple[Dict[str, Any], SimulationSet]]:
        return zip(self.configs, self.sims)

    def __iter__(self) -> Iterator[SimulationSet]:
        return self.sims.__iter__()

    def __len__(self) -> int:
        return len(self.sims)
