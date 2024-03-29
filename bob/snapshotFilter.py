from typing import Optional, List, Union
from bob.simulation import Simulation
from bob.snapshot import Snapshot


class SnapshotFilter:
    def __init__(self, values: Optional[List[Union[int, str]]]) -> None:
        self.values = None if values is None else [int(x) for x in values]

    def get_snapshots(self, sim: Simulation) -> List[Snapshot]:
        if self.values is None:
            return sim.snapshots
        else:
            return [snap for snap in sim.snapshots if int(snap.getName()) in self.values]
