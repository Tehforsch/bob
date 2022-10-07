import yaml
from typing import Tuple, Iterator, Optional, Callable
from pathlib import Path
import os
from time import sleep
import uuid
import shutil
import traceback

from bob.plotter import Plotter
from bob.postprocess import runFunctionsWithPlotter, create_pic_folder
from bob.simulationSet import getSimsFromFolders, SimulationSet
from bob.postprocess import getFunctionsFromPlotConfigs
from bob.config import picFolder
from bob.plotter import PlotName, PlotFilter, PlotFilters

SLEEP_TIMEOUT = 0.1


class PlotFailedException(BaseException):
    def __init__(self, msg: str) -> None:
        self.msg = msg

    def __repr__(self) -> str:
        return self.msg

    pass


class Command(dict):
    def write(self, commFolder: Path) -> None:
        self["id"] = str(uuid.uuid1())
        filename = commFolder / self["id"]
        yaml.dump(self, filename.open("w"))

    @property
    def simFolder(self) -> Path:
        return self["simFolder"]


def getFinishedCommand(postCommand: Command) -> Command:
    return Command({"postCommandId": postCommand["id"], "type": "finished"})


def getErrorCommand(postCommand: Command, error: str) -> Command:
    return Command({"postCommandId": postCommand["id"], "type": "error", "error": error})


def getReplotCommand(postCommand: Command, simFolder: Path, finishedPlotName: PlotName) -> Command:
    return Command({"simFolder": simFolder, "finishedPlotName": finishedPlotName, "type": "replot", "postCommandId": postCommand["id"]})


def getPostCommand(simFolder: Path, config: dict) -> Command:
    return Command({"simFolder": simFolder, "config": config, "type": "post"})


def runPostCommand(command: Command, commFolder: Path, workFolder: Path) -> None:
    try:
        relativePath = command.simFolder
        absolutePath = workFolder / relativePath
        if not absolutePath.is_dir():
            raise ValueError(f"No folder at {absolutePath}")
        simFolders = [absolutePath]
        sims = getSimsFromFolders(simFolders)
        create_pic_folder(absolutePath)
        functions = getFunctionsFromPlotConfigs(command["config"])
        plotter = Plotter(absolutePath, sims, True, False)
        for finishedPlotName in runFunctionsWithPlotter(plotter, functions):
            replotCommand = getReplotCommand(command, relativePath, finishedPlotName)
            replotCommand.write(commFolder)
        finishedCommand = getFinishedCommand(command)
        finishedCommand.write(commFolder)
    except Exception as e:
        errorMessage = traceback.format_exc()
        errorCommand = getErrorCommand(command, str(errorMessage))
        errorCommand.write(commFolder)
        raise e


def runReplotCommand(command: Command, commFolder: Path, remoteWorkFolder: Path, simFolder: Path, show: bool) -> None:
    plotName = command["finishedPlotName"]
    sourcePicFolder = remoteWorkFolder / command["simFolder"] / picFolder
    sourcePlotName = plotName.withPicFolder(sourcePicFolder)
    sourceFolder = sourcePlotName.dataFolder()
    targetPicFolder = simFolder / picFolder
    plotName = plotName.withPicFolder(targetPicFolder)
    targetFolder = plotName.dataFolder()
    targetFolder.mkdir(parents=True, exist_ok=True)
    shutil.copytree(sourceFolder, targetFolder, dirs_exist_ok=True)
    plotter = Plotter(simFolder, SimulationSet([]), True, show)
    print(plotName.qualifiedName)
    plotter.replot(PlotFilters([PlotFilter(qualifiedName=plotName.qualifiedName)]), False, None)


def watchPost(commFolder: Path, workFolder: Path) -> None:
    while True:
        command = getNextCommandOfType(commFolder, "post")
        if command is not None:
            return runPostCommand(command, commFolder, workFolder)
        sleep(SLEEP_TIMEOUT)


def watchReplot(commFolder: Path, remoteWorkFolder: Path, simFolder: Path, postCommandId: Optional[str], show: bool) -> None:
    checkCommandId = lambda type_, command: command["type"] == type_ and (postCommandId is None or command["postCommandId"] == postCommandId)
    while True:
        error = getNextCommandWithPredicate(commFolder, lambda command: checkCommandId("error", command))
        if error is not None:
            raise PlotFailedException(error["error"])
        command = getNextCommandWithPredicate(commFolder, lambda command: checkCommandId("replot", command))
        if command is not None:
            runReplotCommand(command, commFolder, remoteWorkFolder, simFolder, show)
        else:
            command = getNextCommandWithPredicate(commFolder, lambda command: checkCommandId("finished", command))
            if command is not None:
                return
        sleep(SLEEP_TIMEOUT)


def getCommandsAndFiles(commFolder: Path) -> Iterator[Tuple[Command, Path]]:
    for f in (commFolder / f for f in os.listdir(commFolder)):
        try:
            d = yaml.load(f.open("r"), Loader=yaml.Loader)
            yield Command(d), f
        except FileNotFoundError:
            continue


def getNextCommandOfType(commFolder: Path, type_: str) -> Optional[Command]:
    return getNextCommandWithPredicate(commFolder, lambda command: command["type"] == type_)


def getNextCommandWithPredicate(commFolder: Path, predicate: Callable[[Command], bool]) -> Optional[Command]:
    commandsAndFiles = getCommandsAndFiles(commFolder)
    for (command, f) in commandsAndFiles:
        if predicate(command):
            f.unlink()
            return command
    return None
