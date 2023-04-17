from pathlib import Path
import os


class RaxiomSnapshot:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.filenames = [path / f for f in os.listdir(path)]
        self.name = path.name

    pass
