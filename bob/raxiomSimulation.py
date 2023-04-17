from pathlib import Path
import yaml
from bob.raxiomSnapshot import RaxiomSnapshot
from bob.util import getFolders
from bob.baseSim import BaseSim


def getParams(folder: Path):
    filename = folder / "output" / "parameters.yml"
    with open(filename, "r") as f:
        return yaml.safe_load(f)


class RaxiomSimulation(BaseSim):
    def __init__(self, folder: Path) -> None:
        self.folder = folder
        self.params = getParams(folder)
        self.label = self.params.get("simLabel")

    @property
    def outputDir(self) -> Path:
        output_dir = self.params["output"].get("output_dir")
        if output_dir is None:
            name = "output"
        else:
            name = output_dir
        return Path(self.folder, name)

    @property
    def snapshotDir(self) -> Path:
        return self.outputDir / "snapshots"

    @property
    def snapshots(self) -> list[RaxiomSnapshot]:
        snapshotFolders = list(getFolders(self.snapshotDir))

        snapshotFolders.sort(key=lambda x: int(x.name))
        return [RaxiomSnapshot(s) for s in snapshotFolders]
