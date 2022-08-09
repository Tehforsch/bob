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
        args = ["python", str(pybobPath), "--hide", "plot", ".", "plot.bob"]
    else:
        args = ["python", str(pybobPath), "--hide", "replot", "."]
    try:
        subprocess.check_call(args, cwd=folder, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        # Welcome to the worlds laziest error handling but I can't be bothered to find out
        # how to properly handle stdout/stderr in subprocess
        subprocess.check_call(args, cwd=folder)
