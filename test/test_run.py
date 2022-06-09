import os
import unittest
import shutil
import tempfile
from pathlib import Path
import subprocess


class Test(unittest.TestCase):
    def test_runs(self) -> None:
        thisPath = Path(__file__)
        testPath = thisPath.parent / ".." / "testSetups"
        self.pybobPath = thisPath.parent / ".." / "main.py"
        for folder in os.listdir(testPath):
            self.runTestInTemporaryDirectory(testPath / folder)

    def readArgs(self, folder: Path) -> str:
        with open(folder / "args", "r") as f:
            return f.readlines()[0].replace("\n", "")

    def runTestInTemporaryDirectory(self, folder: Path) -> None:
        print(f"Running {folder}")
        with tempfile.TemporaryDirectory() as f:
            shutil.copytree(folder, f, dirs_exist_ok=True)
            self.runTest(Path(f))

    def runTest(self, folder: Path) -> None:
        args = self.readArgs(folder)
        subprocess.check_call(["python", self.pybobPath, *args.split(" ")], cwd=folder)
