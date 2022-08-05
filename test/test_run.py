import os
import unittest
import shutil
import tempfile
from pathlib import Path
import subprocess
from bob.pool import runInPool


class Test(unittest.TestCase):
    def test_runs(self) -> None:
        thisPath = Path(__file__)
        testPath = thisPath.parent / ".." / "testSetups"
        pybobPath = thisPath.parent / ".." / "main.py"
        folders = [testPath / f for f in os.listdir(testPath)]
        runInPool(runTestInTemporaryDirectory, folders, pybobPath)

def runTestInTemporaryDirectory(pybobPath: Path, folder: Path) -> None:
    with tempfile.TemporaryDirectory() as f:
        shutil.copytree(folder, f, dirs_exist_ok=True)
        runTest(Path(f), pybobPath)

def runTest(folder: Path, pybobPath: Path) -> None:
    if (folder / "plot.bob").is_file():
        subprocess.check_call(["python", pybobPath, "plot", ".", "plot.bob"], cwd=folder)
    else:
        subprocess.check_call(["python", pybobPath, "replot", ".", "replot.bob"], cwd=folder)
