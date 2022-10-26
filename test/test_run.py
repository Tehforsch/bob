from typing import List, Any, Union
from time import sleep
import threading
import os
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
        ]
        folders = [self.testPath / f for f in tests]
        runInPool(runTestInTemporaryDirectory, folders, self.pybobPath)

    def test_watch(self) -> None:
        folder = self.testPath / "watch"
        with tempfile.TemporaryDirectory() as comm:
            with tempfile.TemporaryDirectory() as post:
                with tempfile.TemporaryDirectory() as plot:

                    def remotePlot() -> None:
                        plotArgs = ["python", self.pybobPath, "--hide", "remotePlot", comm, post, plot, plotFolder, folder / "plot.bob"]
                        assert runCommand(transform(plotArgs), "remotePlot failed", cwd=plotFolder)

                    # Copy data to postprocessing folder
                    shutil.copytree(folder, Path(post) / "watch", dirs_exist_ok=True)
                    # Create plot file at destination
                    plotFolder = Path(plot) / "watch"
                    os.mkdir(plotFolder)
                    shutil.copy(folder / "plot.bob", plotFolder / "plot.bob")
                    t = threading.Thread(target=remotePlot)
                    t.start()
                    sleep(0.5)
                    postArgs = ["python", self.pybobPath, "watchPost", comm, post]
                    assert runCommand(transform(postArgs), "watchPost failed")
                    t.join(3)


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
