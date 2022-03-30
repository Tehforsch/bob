import os
import pickle
from typing import Iterator, List, Optional, Callable
import itertools
from pathlib import Path
import argparse
import matplotlib.pyplot as plt
import logging
import numpy as np

from bob.postprocessingFunctions import (
    SetFn,
    MultiSetFn,
    SnapFn,
    SliceFn,
)
from bob.simulationSet import SimulationSet
from bob.snapshot import Snapshot
from bob import config
import bob.plots.ionization
from bob.simulation import Simulation
from bob.result import Result
from bob.postprocessingFunctions import PostprocessingFunction


def isSameSnapshot(arg_snap: str, snap: Snapshot) -> bool:
    try:
        if type(snap.number) == int:
            arg_num = int(arg_snap)
            return snap.number == arg_num
        else:
            assert type(snap.number) == tuple
            arg_tuple = tuple(int(x) for x in arg_snap.split(","))
            return snap.number == arg_tuple
    except ValueError:
        raise ValueError("WRONG type of snapshot argument. Either pass an int or int,int for subbox snapshots")


class Plotter:
    def __init__(
        self,
        parent_folder: Path,
        sims: SimulationSet,
        snapshotFilter: List[str],
        show: bool,
        select: Optional[List[str]],
        quotient_params: Optional[List[str]],
    ) -> None:
        self.pic_folder = parent_folder / config.picFolder
        self.data_folder = self.pic_folder / "plots"
        self.sims = self.filterSims(sims, select)
        self.snapshotFilter = snapshotFilter
        self.show = show
        self.quotient_params = quotient_params

    def filterSims(self, sims: SimulationSet, select: Optional[List[str]]) -> SimulationSet:
        if select is None:
            return sims
        else:
            return SimulationSet(sim for sim in sims if sim.name in select)

    def replot(self, args: argparse.Namespace) -> None:
        for plot in os.listdir(self.data_folder):
            plot_folder = self.data_folder / plot
            plot = pickle.load(open(plot_folder / config.plotSerializationFileName, "rb"))
            result = Result.fromFolder(plot_folder)
            plot.plot(plt, result)
            self.saveAndShow(plot_folder.name)

    def runPostAndPlot(
        self, args: argparse.Namespace, fn: PostprocessingFunction, name: str, post: Callable[[], Result], plot: Callable[[plt.axes, Result], None]
    ) -> None:
        logging.info("Running {}".format(name))
        result = post()
        self.save(fn, name, result)
        if not args.post:
            plot(plt, result)
            self.saveAndShow(name)

    def save(self, fn: PostprocessingFunction, plotName: str, result: Result) -> None:
        plotDataFolder = self.data_folder / plotName
        plotDataFolder.mkdir(parents=True, exist_ok=True)
        self.savePlotInfo(fn, plotDataFolder)
        self.saveResult(result, plotDataFolder)

    def savePlotInfo(self, fn: PostprocessingFunction, plotDataFolder: Path) -> None:
        filename = plotDataFolder / config.plotSerializationFileName
        pickle.dump(fn, open(filename, "wb"))

    def saveResult(self, result: Result, plotDataFolder: Path) -> None:
        result.save(plotDataFolder)

    def getQuotient(self) -> [SimulationSet]:
        quotient_params = self.quotient_params
        if quotient_params is None:
            quotient_params = []
        print(self.sims.quotient(quotient_params))
        return self.sims.quotient(quotient_params)

    def runMultiSetFn(self, args: argparse.Namespace, function: MultiSetFn) -> None:
        quotient = [sims for (config, sims) in self.getQuotient()]
        logging.info("Running {}".format(function.name))
        self.runPostAndPlot(args, function, function.name, lambda: function.post(args, quotient), function.plot)

    def runSetFn(self, args: argparse.Namespace, function: MultiSetFn) -> None:
        quotient = self.getQuotient()
        logging.info("Running {}".format(function.name))
        for (i, (config, sims)) in enumerate(quotient):
            logging.info("For set {}".format(config))
            self.runPostAndPlot(args, function, f"{i}_{function.name}", lambda: function.post(args, sims), function.plot)

    def runSnapFn(self, args: argparse.Namespace, function: SnapFn) -> None:
        logging.info("Running {}".format(function.name))
        for sim in self.sims:
            logging.info("For sim {}".format(sim.name))
            for snap in self.get_snapshots(sim):
                logging.info("For snap {}".format(snap.name))
                name = "{}_{}_{}".format(function.getName(args), sim.name, snap.name)
                self.runPostAndPlot(args, function, name, lambda: function.post(args, sim, snap), function.plot)

    def runSlicePlotFunction(self, function: SliceFn) -> None:
        logging.info("Running {}".format(function.name))
        for sim in self.sims:
            logging.info("For sim {}".format(sim.name))
            for slice_ in sim.getSlices(function.slice_type):
                logging.info("For slice {}".format(slice_.name))
                function(plt, sim, slice_)
                self.saveAndShow(
                    "{}_{}_{}".format(sim.name, function.name, slice_.name),
                )

    def isInSnapshotArgs(self, snap: Snapshot) -> bool:
        return self.snapshotFilter is None or any(isSameSnapshot(arg_snap, snap) for arg_snap in self.snapshotFilter)

    def get_snapshots(self, sim: Simulation) -> Iterator[Snapshot]:
        for snap in sim.snapshots:
            if self.isInSnapshotArgs(snap):
                yield snap

    def saveAndShow(self, filename: str) -> None:
        filepath = self.pic_folder / filename
        filepath.parent.mkdir(exist_ok=True)
        plt.savefig(str(filepath) + ".pdf", dpi=config.dpi)
        if self.show:
            plt.show()
        plt.clf()
