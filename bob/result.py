import os
from typing import Iterator, Any, Union, List
import shutil
from pathlib import Path

import numpy as np
import astropy.units as pq

numpyFileEnding = ".npy"
unitFileEnding = ".unit"


def listdir(folder: Path) -> Iterator[Path]:
    return (folder / f for f in os.listdir(folder))


def getFolders(folder: Path) -> Iterator[Path]:
    return (f for f in listdir(folder) if f.is_dir())


def getFilesWithSuffix(folder: Path, suffix: str) -> Iterator[Path]:
    return (folder / f for f in os.listdir(folder) if Path(f).suffix == suffix)


def getNpyFiles(folder: Path) -> Iterator[Path]:
    return getFilesWithSuffix(folder, numpyFileEnding)


def readUnit(filename: Path) -> pq.Unit:
    with open(filename, "r") as f:
        return pq.Unit(f.readline().replace("\n", ""))


def readQuantity(filenameBase: Path) -> pq.Quantity:
    numpyFileName = filenameBase.with_suffix(numpyFileEnding)
    unitFileName = filenameBase.with_suffix(unitFileEnding)
    unit = readUnit(unitFileName)
    return np.load(numpyFileName) * unit


def readQuantityFromNumpyFilePath(numpyFilePath: Path) -> pq.Quantity:
    return readQuantity(numpyFilePath.with_suffix(""))


def saveUnit(filename: Path, unit: pq.UnitBase) -> None:
    with open(filename, "w") as f:
        f.write(str(unit))


def saveQuantity(filenameBase: Path, quantity: pq.Quantity) -> None:
    dataFileName = filenameBase.with_suffix(numpyFileEnding)
    unitFileName = filenameBase.with_suffix(unitFileEnding)
    np.save(dataFileName, quantity.value)
    saveUnit(unitFileName, quantity.unit)


def saveQuantityList(folder: Path, quantities: List[pq.Quantity]) -> None:
    folder.mkdir()
    for (i, quantity) in enumerate(quantities):
        assert type(quantity) == pq.Quantity, f"Wrong type in list result: {type(quantity)}"
        saveQuantity(folder / str(i), quantity)


def saveResultList(folder: Path, quantities: List["Result"]) -> None:
    folder.mkdir()


def filenameBase(folder: Path, quantityName: str) -> Path:
    return folder / f"{quantityName}"


class Result:
    def __init__(self) -> None:
        pass

    def delete_old_files(self, folder: Path) -> None:
        files = (folder / f for f in os.listdir(folder)) 
        toRemove = (f for f in files if f.is_dir() or f.stem in [numpyFileEnding, unitFileEnding])
        for f in toRemove:
            shutil.rmtree(f)
            
    def save(self, folder: Path) -> None:
        self.delete_old_files(folder)
        folder.mkdir(exist_ok=True)
        for (name, quantity) in self.__dict__.items():
            if type(quantity) == pq.Quantity:
                saveQuantity(filenameBase(folder, name), quantity)
            elif type(quantity) == list:
                if type(quantity[0]) == pq.Quantity:
                    saveQuantityList(filenameBase(folder, name), quantity)
                elif isinstance(quantity[0], Result):
                    saveResultList(filenameBase(folder, name), quantity)
            elif type(quantity) == np.ndarray:
                raise ValueError("Refusing to save array without units")
            else:
                raise ValueError(f"Currently unsupported type: {type(quantity)}")

    @staticmethod
    def readFromFolder(folder: Path) -> "Result":
        result = Result()
        for f in getNpyFiles(folder):
            result.__setattr__(f.stem, readQuantityFromNumpyFilePath(f))
        for subdir in getFolders(folder):
            arrs = []
            for f in sorted(getNpyFiles(subdir), key=lambda f: int(f.stem)):
                arrs.append(readQuantityFromNumpyFilePath(f))
            result.__setattr__(subdir.stem, arrs)
        return result

    def __repr__(self) -> str:
        def formatField(name: str, value: Union[pq.Quantity, List[pq.Quantity]]) -> str:
            if type(value) == pq.Quantity:
                return f"{name:<15} [{value.unit:>10}]: {value.value}"
            elif type(value) == Result:
                return value.__repr__()
            elif type(value) == list:
                return "\n".join(formatField(name, x) for x in value)
            else:
                raise ValueError("Wrong type in result: {}", type(value))

        return "\n".join(formatField(name, value) for (name, value) in self.__dict__.items())

    def __setattr__(self, name: str, value: Union[pq.Quantity, List[pq.Quantity]]) -> None:
        object.__setattr__(self, name, value)

    def __getattr__(self, name: str) -> Any:
        object.__getattribute__(self, name)
