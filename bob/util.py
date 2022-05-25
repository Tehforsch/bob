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
    unit = quantities[0].unit
    return np.array((y / unit).decompose().value for y in quantities) * unit
