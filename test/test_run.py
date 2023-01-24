from typing import List, Any, Union
import unittest
import shutil
import tempfile
from pathlib import Path
import subprocess
from bob.pool import runInPool


def transform(l: List[Union[Any, str]]) -> List[str]:
    return [str(x) for x in l]


def runCommand(args: List[str], message: str, **kwargs: Any) -> bool:
    try:
        subprocess.check_call(args, **kwargs, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except:
        # Welcome to the worlds laziest error handling but I can't be bothered to find out
        # how to properly handle stdout/stderr in subprocess
        subprocess.check_call(args, **kwargs)
        return False


class Test(unittest.TestCase):
    def setUp(self) -> None:
        self.thisPath = Path(__file__)
        self.testPath = self.thisPath.parent / ".." / "testSetups"
        self.pybobPath = self.thisPath.parent / ".." / "main.py"

    def test_runs(self) -> None:
        tests = [
            "bobSlice",
            "combinedFieldSlice",
            "ionizationTime",
            "meanFieldOverTimeInternalEnergy",
            "multipleSlices",
            "multipleSlicesSubstitutions",
            "replot",
            "sliceWithStarParticles",
            "sourcePosition",
            "temperatureDensityHistogram",
            "temperatureIonizationHistogram",
            "sourceField",
            "luminosityOverHaloMass",
            "resolvedEscapeFraction",
        ]
        folders = [self.testPath / f for f in tests]
        runInPool(runTestInTemporaryDirectory, folders, self.pybobPath)


def runTestInTemporaryDirectory(pybobPath: Path, folder: Path) -> None:
    with tempfile.TemporaryDirectory() as f:
        shutil.copytree(folder, f, dirs_exist_ok=True)
        runTest(Path(f), pybobPath, folder.name)


def runTest(folder: Path, pybobPath: Path, testName: str) -> None:
    print("running", testName)
    if (folder / "plot.bob").is_file():
        args = ["python", str(pybobPath), "--hide", "plot", ".", "plot.bob"]
    else:
        args = ["python", str(pybobPath), "--hide", "replot", "."]
    assert runCommand(args, f"Test {testName} failed", cwd=folder)
