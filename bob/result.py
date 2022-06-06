import os
import tempfile
from typing import Iterator, Any, Union, List
import shutil
from pathlib import Path

import unittest
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

    def save(self, folder: Path) -> None:
        shutil.rmtree(folder)
        folder.mkdir()
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
            elif type(value) == list:
                return "\n".join(formatField(name, x) for x in value)
            else:
                raise ValueError("Wrong type in result: {}", type(value))

        return "\n".join(formatField(name, value) for (name, value) in self.__dict__.items())

    def __setattr__(self, name: str, value: Union[pq.Quantity, List[pq.Quantity]]) -> None:
        object.__setattr__(self, name, value)

    def __getattr__(self, name: str) -> Any:
        object.__getattribute__(self, name)


class Tests(unittest.TestCase):
    @staticmethod
    def getTestResultA() -> Any:
        class A(Result):
            def __init__(self) -> None:
                self.temperature = np.array([1.0, 2.0, 3.0]) * pq.K
                self.lengths = np.array([1.0, 0.0, 0.0]) * pq.m

        return A()

    @staticmethod
    def getTestResultB() -> Any:
        class B(Result):
            def __init__(self) -> None:
                self.densities = [
                    np.array([1.0, 0.0]) * pq.kg / pq.m**3,
                    np.array([2.0, 5.0, 1.0]) * pq.g / pq.m**3,
                    np.array([3.0, 2.0]) * pq.kg / pq.m**3,
                ]
                self.volumes = np.array([0.0, 0.0]) * pq.cm**3
                self.some_other = np.array([5.0, 1.0]) * pq.J

        return B()

    @staticmethod
    def getTestResultC() -> Any:
        class C(Result):
            def __init__(self) -> None:
                self.results = [Tests.getTestResultA(), Tests.getTestResultB()]

        return C()

    def check_write_and_read_result(self, result: Result) -> None:
        with tempfile.TemporaryDirectory() as f:
            folder = Path(f)
            result.save(folder)
            resultRead = Result.readFromFolder(folder)
            self.assert_equal_results(result, resultRead)

    def test_a(self) -> None:
        self.check_write_and_read_result(self.getTestResultA())

    def test_b(self) -> None:
        self.check_write_and_read_result(self.getTestResultB())

    def test_c(self) -> None:
        self.check_write_and_read_result(self.getTestResultC())

    def assert_equal_quantities(self, q1: pq.Quantity, q2: pq.Quantity) -> None:
        assert q1.unit == q2.unit
        assert np.equal(q1.value, q2.value).all()

    def assert_result_contains_other_result(self, res1: Result, res2: Result) -> None:
        for (k, v) in res1.__dict__.items():
            assert k in res2.__dict__
            if type(v) == pq.Quantity:
                self.assert_equal_quantities(res2.__getattribute__(k), v)
            else:
                for (q1, q2) in zip(res2.__getattribute__(k), v):
                    self.assert_equal_quantities(q1, q2)

    def assert_equal_results(self, res1: Result, res2: Result) -> None:
        self.assert_result_contains_other_result(res1, res2)
        self.assert_result_contains_other_result(res2, res1)


if __name__ == "__main__":
    unittest.main()
