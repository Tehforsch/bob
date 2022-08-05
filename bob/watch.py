from typing import Sequence
from pathlib import Path
import os
from time import sleep

from bob.plotter import Plotter
from bob.postprocess import runFunctionsWithPlotter, readPlotFile, create_pic_folder
from bob.simulationSet import getSimsFromFolders


def runPlots(commFolder: Path, files: Sequence[Path]) -> None:
    for f in files:
        f = commFolder / f
        path = Path(f.name.replace("##", "/"))  # amazing stuff
        if not path.is_dir():
            raise ValueError(f"No folder at {path}")
            continue
        simFolders = [path]
        sims = getSimsFromFolders(simFolders)
        create_pic_folder(path)
        functions = readPlotFile(f, True)
        plotter = Plotter(path, sims, True, False)
        runFunctionsWithPlotter(plotter, functions)
        f.unlink()


def watch(commFolder: Path, workFolder: Path) -> None:
    while True:
        files = os.listdir(commFolder)
        if len(files) > 0:
            runPlots(commFolder, list(Path(f) for f in files))
        sleep(1)
