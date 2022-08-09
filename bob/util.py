from typing import List
import itertools
import subprocess
import logging

from math import log10
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


def zeroPadToLength(num: int, numSims: int) -> str:
    padding = int(log10(int(numSims))) + 1
    return "{:0{padding}}".format(num, padding=padding)


def showImageInTerminal(path: Path) -> None:
    width = 600
    height = 400
    tmpfile = Path("/tmp/test.png")
    args = ["convert", str(path), "-scale", f"{width}x{height}", str(tmpfile)]
    subprocess.check_call(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    args = ["kitty", "+kitten", "icat", "--silent", "--transfer-mode", "file", str(tmpfile)]
    logging.debug(path)
    subprocess.check_call(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
