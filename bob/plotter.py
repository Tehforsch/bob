import os
import yaml
from typing import Iterator, List, Optional, Callable, Union
from pathlib import Path
import argparse
import matplotlib.pyplot as plt
import logging

from bob.postprocessingFunctions import (
    SetFn,
    MultiSetFn,
    SnapFn,
    SliceFn,
)
from bob.simulationSet import SimulationSet, Single
from bob.snapshot import Snapshot
import bob.config
from bob.simulation import Simulation
from bob.result import Result
from bob.postprocessingFunctions import PostprocessingFunction
from bob.multiSet import MultiSet
from bob.pool import runInPool

QuotientParams = Optional[Union[List[str], Single]]


def walkfiles(path: Path) -> Iterator[Path]:
    for root, dirs, files in os.walk(path):
        for f in files:
            yield Path(root) / f


def isSameSnapshot(arg_snap: str, snap: Snapshot) -> bool:
    try:
        arg_num = int(arg_snap)
        return snap.number.value == arg_num
    except ValueError:
        raise ValueError("WRONG type of snapshot argument. Need an integer")


def getOutputFilename(filename: str, outputFileType: str) -> Path:
    return Path("{}.{}".format(filename, outputFileType))


class Plotter:
    def __init__(
        self,
        parent_folder: Path,
        sims: SimulationSet,
        postprocess_only: bool,
        show: bool,
    ) -> None:
        self.picFolder = parent_folder / bob.config.picFolder
        self.sims = sims
        self.dataFolder = self.picFolder / "plots"
        self.postprocess_only = postprocess_only
        self.show = show

    def filterSims(self, select: Optional[List[str]]) -> SimulationSet:
        if select is None:
            return self.sims
        else:
            return SimulationSet(sim for sim in self.sims if sim.name in select)

    def isNew(self, plotName: str) -> bool:
        images = [(self.picFolder / plotName).with_suffix(suffix) for suffix in bob.config.possibleImageSuffixes]
        images = [image for image in images if image.is_file()]
        if len(images) == 0:
            return True
        else:
            plotPath = self.dataFolder / plotName
            print(plotPath)
            for f in walkfiles(plotPath):
                print(f)
            mtimePlot = max(os.path.getmtime(str(f)) for f in walkfiles(plotPath))
            mtimeImage = max(os.path.getmtime(image) for image in images)
            return mtimeImage < mtimePlot

    def getNewPlots(self) -> List[str]:
        plots = os.listdir(self.dataFolder)
        return [plot for plot in plots if self.isNew(plot)]

    def replot(self, args: argparse.Namespace) -> None:
        if args.onlyNew:
            plots = self.getNewPlots()
        else:
            plots = os.listdir(self.dataFolder)
        plots.sort()
        runInPool(runPlot, plots, self, args)

    def runPostAndPlot(self, fn: PostprocessingFunction, name: str, post: Callable[[], Result], plot: Callable[[plt.axes, Result], None]) -> str:
        logging.info("Running {}".format(name))
        result = post()
        self.save(fn, name, result)
        if not self.postprocess_only:
            plot(plt, result)
            self.saveAndShow(name, fn)
        return name

    def save(self, fn: PostprocessingFunction, plotName: str, result: Result) -> None:
        plotDataFolder = self.dataFolder / plotName
        plotDataFolder.mkdir(parents=True, exist_ok=True)
        self.savePlotInfo(fn, plotDataFolder)
        self.saveResult(result, plotDataFolder)

    def savePlotInfo(self, fn: PostprocessingFunction, plotDataFolder: Path) -> None:
        filename = plotDataFolder / bob.config.plotSerializationFileName
        yaml.dump({fn.name: dict(fn.config.items())}, open(filename, "w"))

    def saveResult(self, result: Result, plotDataFolder: Path) -> None:
        result.save(plotDataFolder)

    def getQuotient(self, quotient_params: QuotientParams, sims_filter: Optional[List[str]], labels: Optional[List[str]]) -> MultiSet:
        if quotient_params is None:
            quotient_params = []
        sims = self.filterSims(sims_filter)
        return MultiSet(sims.quotient(quotient_params), labels)

    def runMultiSetFn(self, function: MultiSetFn) -> Iterator[str]:
        quotient = self.getQuotient(function.config["quotient"], function.config["sims"], function.config["labels"])
        logging.info("Running {}".format(function.name))
        yield self.runPostAndPlot(function, function.getName(), lambda: function.post(quotient), function.plot)

    def runSetFn(self, function: SetFn) -> Iterator[str]:
        quotient = self.getQuotient(function.config["quotient"], function.config["sims"], function.config["labels"])
        logging.info("Running {}".format(function.name))
        for (i, (config, sims)) in enumerate(quotient.iterWithConfigs()):
            logging.info("For set {}".format(i))
            yield self.runPostAndPlot(function, f"{i}_{function.getName()}", lambda: function.post(sims), function.plot)

    def runSnapFn(self, function: SnapFn) -> Iterator[str]:
        logging.info("Running {}".format(function.name))
        for sim in self.filterSims(function.config["sims"]):
            logging.info("For sim {}".format(sim.name))
            for snap in self.get_snapshots(sim, function.config["snapshots"]):
                logging.info("For snap {}".format(snap.name))
                name = "{}_{}_{}".format(function.getName(), sim.name, snap.name)
                yield self.runPostAndPlot(function, name, lambda: function.post(sim, snap), function.plot)

    def runSliceFn(self, function: SliceFn) -> Iterator[str]:
        logging.info("Running {}".format(function.name))
        for sim in self.filterSims(function.config["sims"]):
            logging.info("For sim {}".format(sim.name))
            for slice_ in sim.getSlices(function.config["field"]):
                if function.config["snapshots"] is None or any(arg_snap == slice_.name for arg_snap in function.config["snapshots"]):
                    logging.info("For slice {}".format(slice_.name))
                    name = "{}_{}_{}".format(function.getName(), sim.name, slice_.name)
                    yield self.runPostAndPlot(function, name, lambda: function.post(sim, slice_), function.plot)

    def isInSnapshotArgs(self, snapshotFilter: Optional[List[str]], snap: Snapshot) -> bool:
        return snapshotFilter is None or any(isSameSnapshot(arg_snap, snap) for arg_snap in snapshotFilter)

    def get_snapshots(self, sim: Simulation, snapshotFilter: Optional[List[str]]) -> Iterator[Snapshot]:
        for snap in sim.snapshots:
            if self.isInSnapshotArgs(snapshotFilter, snap):
                yield snap

    def saveAndShow(self, filename: str, fn: PostprocessingFunction) -> None:
        filepath = self.picFolder / getOutputFilename(filename, fn.config["outputFileType"])
        filepath.parent.mkdir(exist_ok=True)
        plt.savefig(str(filepath), dpi=bob.config.dpi)
        if self.show:
            plt.show()
        plt.clf()


def getBaseName(plotName: str) -> str:
    if not "_" in plotName:
        return plotName
    return plotName[: plotName.index("_")]


# Needs to be a top-level function so it can be used by multiprocessing
def runPlot(plotter: Plotter, args: argparse.Namespace, plotName: str) -> None:
    from bob.postprocess import readPlotFile

    baseName = getBaseName(plotName)
    if (args.plots is None or plotName in args.plots) and (args.types is None or baseName in args.types):
        print("Replotting", plotName)
        plotFolder = plotter.dataFolder / plotName
        functions = readPlotFile(plotFolder / bob.config.plotSerializationFileName, False)
        assert len(functions) == 1, "More than one plot in replot information."
        result = Result.readFromFolder(plotFolder)
        functions[0].plot(plt, result)
        plotter.saveAndShow(plotFolder.name, functions[0])
