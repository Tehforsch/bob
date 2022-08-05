import yaml
from typing import Tuple, Iterator, Any
from pathlib import Path
import os
from time import sleep
import uuid
import shutil

from bob.plotter import Plotter
from bob.postprocess import runFunctionsWithPlotter, create_pic_folder
from bob.simulationSet import getSimsFromFolders, SimulationSet
from bob.postprocess import getFunctionsFromPlotConfigs
from bob.config import picFolder


class Command(dict):
    def write(self, commFolder: Path) -> None:
        filename = commFolder / str(uuid.uuid1())
        yaml.dump(self, filename.open("w"))

    @property
    def simFolder(self) -> Path:
        return self["simFolder"]


def getReplotCommand(simFolder: Path, finishedPlotName: str) -> Command:
    return Command({"simFolder": simFolder, "finishedPlotName": finishedPlotName, "type": "replot"})


def runPostCommand(command: Command, commFolder: Path, workFolder: Path) -> None:
    if not command.simFolder.is_dir():
        raise ValueError(f"No folder at {command.simFolder}")
    simFolders = [command.simFolder]
    sims = getSimsFromFolders(simFolders)
    create_pic_folder(command.simFolder)
    functions = getFunctionsFromPlotConfigs(command["config"])
    plotter = Plotter(command.simFolder, sims, True, False)
    for finishedPlotName in runFunctionsWithPlotter(plotter, functions):
        replotCommand = getReplotCommand(command.simFolder, finishedPlotName)
        replotCommand.write(commFolder)


def runReplotCommand(command: Command, commFolder: Path, localWorkFolder: Path, remoteWorkFolder: Path) -> None:
    sourceFolder = remoteWorkFolder / command["simFolder"] / picFolder / "plots" / command["finishedPlotName"]
    targetFolder = localWorkFolder / command["simFolder"] / command["finishedPlotName"]
    targetFolder.mkdir(parents=True, exist_ok=True)
    shutil.copytree(sourceFolder, targetFolder, dirs_exist_ok=True)
    plotter = Plotter(command["simFolder"], SimulationSet([]), True, False)
    plotter.replot([command["finishedPlotName"]], False)


def watchPost(commFolder: Path, workFolder: Path) -> None:
    def workFunction(command: Command) -> None:
        runPostCommand(command, commFolder, workFolder)

    watch(workFunction, commFolder, "post")


def watchReplot(commFolder: Path, localWorkFolder: Path, remoteWorkFolder: Path) -> None:
    def workFunction(command: Command) -> None:
        runReplotCommand(command, commFolder, localWorkFolder, remoteWorkFolder)

    watch(workFunction, commFolder, "replot")


def getCommandsAndFiles(commFolder: Path) -> Iterator[Tuple[Command, Path]]:
    for f in (commFolder / f for f in os.listdir(commFolder)):
        try:
            d = yaml.load(f.open("r"), Loader=yaml.Loader)
            yield Command(d), f
        except FileNotFoundError:
            continue


def watch(function: Any, commFolder: Path, commandType: str) -> None:
    while True:
        commandsAndFiles = getCommandsAndFiles(commFolder)
        for (command, f) in commandsAndFiles:
            if command["type"] == commandType:
                function(command)
                f.unlink()
        sleep(1)
