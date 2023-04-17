from pathlib import Path


class BaseSim:
    def __init__(self, folder: Path) -> None:
        self.folder = folder

    @property  # type: ignore
    def name(self) -> str:
        return self.folder.name
