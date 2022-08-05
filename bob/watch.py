from typing import Sequence
import argparse
from pathlib import Path
import os
from time import sleep

import bob.postprocess
from bob.simulationSet import getSimsFromFolders
from bob.util import getCommonParentFolder


def runPlots(args: argparse.Namespace, files: Sequence[Path]) -> None:
    for f in files:
        path = Path(f.name.replace("##", "/"))  # amazing stuff
        if not path.is_dir():
            raise ValueError(f"No folder at {path}")
            continue
        simFolders = [path]
        sims = getSimsFromFolders(simFolders)
        folder = getCommonParentFolder(simFolders)
        bob.postprocess.main(args, folder, sims)


def watch(args: argparse.Namespace, commFolder: Path, workFolder: Path) -> None:
    while True:
        files = os.listdir(commFolder)
        if len(files) > 0:
            runPlots(args, list(Path(f) for f in files))
        sleep(1)
