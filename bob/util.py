from typing import List
import itertools

from pathlib import Path
import numpy as np
import astropy.units as pq


def getCommonParentFolder(folders: List[Path]) -> Path:
    parts = (folder.parts for folder in folders)
    zippedParts = zip(*parts)
    commonParts = (parts[0] for parts in itertools.takewhile(lambda parts: all(part == parts[0] for part in parts), zippedParts))
    return Path(*commonParts)


def getArrayQuantity(quantities: List[pq.Quantity]) -> pq.Quantity:
    unit = 1.0 * quantities[0].unit
    for y in quantities:
        if not (y / unit).decompose().unit == "":
            raise ValueError("Different units in quantity array")
    return np.array([(y / unit).decompose().value for y in quantities]) * unit


def getDataFile(relativePath: str) -> Path:
    thisFolder = Path(__file__).parent
    dataFolder = thisFolder.parent / "data"
    return dataFolder / relativePath
