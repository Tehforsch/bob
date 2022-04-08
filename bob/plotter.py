import os
import pickle
from typing import Iterator, List, Optional, Callable
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
from bob.simulationSet import SimulationSet
from bob.snapshot import Snapshot
import bob.config
from bob.simulation import Simulation
from bob.result import Result, getResultFromFolder
from bob.postprocessingFunctions import PostprocessingFunction
from bob.multiSet import MultiSet


def isSameSnapshot(arg_snap: str, snap: Snapshot) -> bool:
    try:
        arg_num = int(arg_snap)
        return snap.number.value == arg_num
    except ValueError:
        raise ValueError("WRONG type of snapshot argument. Need an integer")


class Plotter:
    def __init__(
        self,
        parent_folder: Path,
        sims: SimulationSet,
        snapshotFilter: List[str],
        show: bool,
        select: Optional[List[str]],
        quotient_params: Optional[List[str]],
        outputFileType: str,
    ) -> None:
        self.picFolder = parent_folder / bob.config.picFolder
        self.dataFolder = self.picFolder / "plots"
        self.sims = self.filterSims(sims, select)
        self.snapshotFilter = snapshotFilter
        self.show = show
        self.quotient_params = quotient_params
        self.outputFileType = outputFileType

    def filterSims(self, sims: SimulationSet, select: Optional[List[str]]) -> SimulationSet:
        if select is None:
            return sims
        else:
            return SimulationSet(sim for sim in sims if sim.name in select)

    def replot(self, args: argparse.Namespace) -> None:
        plots = os.listdir(self.dataFolder)
        plots.sort()
        for plotName in plots:
            if args.plots is None or plotName in args.plots:
                print("Replotting", plotName)
                plotFolder = self.dataFolder / plotName
                plot = pickle.load(open(plotFolder / bob.config.plotSerializationFileName, "rb"))
                result = getResultFromFolder(plotFolder)
                plot.plot(plt, result)
                self.saveAndShow(plotFolder.name)

    def runPostAndPlot(
        self, args: argparse.Namespace, fn: PostprocessingFunction, name: str, post: Callable[[], Result], plot: Callable[[plt.axes, Result], None]
    ) -> None:
        logging.info("Running {}".format(name))
        fn.init(args)
        result = post()
        self.save(fn, name, result)
        if not args.post:
            plot(plt, result)
            self.saveAndShow(name)

    def save(self, fn: PostprocessingFunction, plotName: str, result: Result) -> None:
        plotDataFolder = self.dataFolder / plotName
        plotDataFolder.mkdir(parents=True, exist_ok=True)
        self.savePlotInfo(fn, plotDataFolder)
        self.saveResult(result, plotDataFolder)

    def savePlotInfo(self, fn: PostprocessingFunction, plotDataFolder: Path) -> None:
        filename = plotDataFolder / bob.config.plotSerializationFileName
        pickle.dump(fn, open(filename, "wb"))

    def saveResult(self, result: Result, plotDataFolder: Path) -> None:
        result.save(plotDataFolder)

    def getQuotient(self, labels: Optional[List[str]]) -> MultiSet:
        quotient_params = self.quotient_params
        if quotient_params is None:
            quotient_params = []
        return MultiSet(self.sims.quotient(quotient_params), labels)

    def runMultiSetFn(self, args: argparse.Namespace, function: MultiSetFn) -> None:
        quotient = self.getQuotient(args.labels)
        logging.info("Running {}".format(function.name))
        self.runPostAndPlot(args, function, function.getName(args), lambda: function.post(args, quotient), function.plot)

    def runSetFn(self, args: argparse.Namespace, function: SetFn) -> None:
        quotient = self.getQuotient(args.labels)
        logging.info("Running {}".format(function.name))
        for (i, (config, sims)) in enumerate(quotient.iterWithConfigs()):
            logging.info("For set {}".format(i))
            self.runPostAndPlot(args, function, f"{i}_{function.getName(args)}", lambda: function.post(args, sims), function.plot)

    def runSnapFn(self, args: argparse.Namespace, function: SnapFn) -> None:
        logging.info("Running {}".format(function.name))
        for sim in self.sims:
            logging.info("For sim {}".format(sim.name))
            for snap in self.get_snapshots(sim):
                logging.info("For snap {}".format(snap.name))
                name = "{}_{}_{}".format(function.getName(args), sim.name, snap.name)
                self.runPostAndPlot(args, function, name, lambda: function.post(args, sim, snap), function.plot)

    def runSliceFn(self, args: argparse.Namespace, function: SliceFn) -> None:
        logging.info("Running {}".format(function.name))
        for sim in self.sims:
            logging.info("For sim {}".format(sim.name))
            for slice_ in sim.getSlices(args.slice_field):
                if self.snapshotFilter is None or any(arg_snap == slice_.name for arg_snap in self.snapshotFilter):
                    logging.info("For slice {}".format(slice_.name))
                    name = "{}_{}_{}".format(function.getName(args), sim.name, slice_.name)
                    self.runPostAndPlot(args, function, name, lambda: function.post(args, sim, slice_), function.plot)

    def isInSnapshotArgs(self, snap: Snapshot) -> bool:
        return self.snapshotFilter is None or any(isSameSnapshot(arg_snap, snap) for arg_snap in self.snapshotFilter)

    def get_snapshots(self, sim: Simulation) -> Iterator[Snapshot]:
        for snap in sim.snapshots:
            if self.isInSnapshotArgs(snap):
                yield snap

    def saveAndShow(self, filename: str) -> None:
        filepath = self.picFolder / filename
        filepath.parent.mkdir(exist_ok=True)
        plt.savefig(str(filepath) + self.outputFileType, dpi=bob.config.dpi)
        if self.show:
            plt.show()
        plt.clf()
