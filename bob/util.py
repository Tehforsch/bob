from pathlib import Path
from typing import List, Iterator, Optional
import os
import itertools
import subprocess
import logging

from math import log10
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


def isclose(a: pq.Quantity, b: pq.Quantity, epsilon: Optional[float] = 1e-10) -> bool:
    return abs(a - b) / (a + b) < epsilon


def getDataFile(relativePath: str) -> Path:
    thisFolder = Path(__file__).parent
    dataFolder = thisFolder.parent / "data"
    return dataFolder / relativePath


def zeroPadToLength(num: int, numSims: int) -> str:
    padding = int(log10(int(numSims))) + 1
    return "{:0{padding}}".format(num, padding=padding)


def showImageInTerminal(path: Path) -> None:
    width = 800
    height = 600
    tmpfile = Path("/tmp/test.png")
    args = ["convert", str(path), "-scale", f"{width}x{height}", str(tmpfile)]
    subprocess.check_call(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    args = ["kitty", "+kitten", "icat", "--silent", "--transfer-mode", "file", str(tmpfile)]
    logging.debug(path)
    subprocess.check_call(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def listdir(folder: Path) -> Iterator[Path]:
    return (folder / f for f in os.listdir(folder))


def getFolders(folder: Path) -> Iterator[Path]:
    return (f for f in listdir(folder) if f.is_dir())


def getFiles(folder: Path) -> Iterator[Path]:
    return (f for f in listdir(folder) if f.is_file())


def getFolderNames(folder: Path) -> Iterator[str]:
    return (f.name for f in listdir(folder) if f.is_dir())


def getFilesWithSuffix(folder: Path, suffix: str) -> Iterator[Path]:
    return (folder / f for f in os.listdir(folder) if Path(f).suffix == suffix)


def walkfiles(path: Path) -> Iterator[Path]:
    for root, dirs, files in os.walk(path):
        for f in files:
            yield Path(root) / f
