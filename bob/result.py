import os
import logging

from pathlib import Path
from typing import List
import numpy as np
import astropy.units as pq


def getNpyFiles(folder: Path) -> List[Path]:
    return [folder / f for f in os.listdir(folder) if Path(f).suffix == ".npy"]


class Result:
    def __init__(self, arrs: List[np.ndarray]) -> None:
        self.arrs = arrs

    def save(self, folder: Path) -> None:
        for f in getNpyFiles(folder):
            os.unlink(f)
        for (i, arr) in enumerate(self.arrs):
            if type(arr) == pq.Quantity:
                value = arr.value
                logging.warning(f"Saving array with units: {arr.unit}")
            else:
                value = arr
            np.save(folder / str(i), value)


def getResultFromFolder(folder: Path) -> Result:
    files = getNpyFiles(folder)
    files.sort(key=lambda f: int(f.stem))
    return Result([np.load(f) for f in files])
