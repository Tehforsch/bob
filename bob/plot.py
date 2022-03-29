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

    def runPostAndPlot(self, args: argparse.Namespace, name: str, post: Callable[[], Result], plot: Callable[[plt.axes, Result], None]) -> None:
        logging.info("Running {}".format(name))
        result = post()
        self.saveResult(name, result)
        plot(plt, result)
        self.saveAndShow(name)

    def saveResult(self, plotName, result):
        plotDataFolder = self.data_folder / plotName
        plotDataFolder.mkdir(parents=True, exist_ok=True)
        result.save(plotDataFolder)

    def runMultiSetFn(self, args: argparse.Namespace, function: MultiSetFn) -> None:
        logging.info("Running {}".format(function.name))
        quotient_params = self.quotient_params
        if quotient_params is None:
            quotient_params = []
        print(self.sims.quotient(quotient_params))
        quotient = [sims for (config, sims) in self.sims.quotient(quotient_params)]

        def post():
            print(function.post)
            function.post(args, quotient)

        self.runPostAndPlot(args, function.name, post, function.plot)

    # def runSingleSimPlot(self, function: SingleSimPlotFunction) -> None:
    #     logging.info("Running {}".format(function.name))
    #     for sim in self.sims:
    #         logging.info("For sim {}".format(sim.name))
    #         function(plt, sim)
    #         self.saveAndShow("{}_{}".format(sim.name, function.name))

    def runSnapFn(self, args: argparse.Namespace, function: SnapFn) -> None:
        logging.info("Running {}".format(function.name))
        for sim in self.sims:
            logging.info("For sim {}".format(sim.name))
            for snap in self.get_snapshots(sim):
                logging.info("For snap {}".format(snap.name))
                name = "{}_{}_{}".format(sim.name, function.name, snap.name)
                self.runPostAndPlot(args, name, lambda: function.post(args, sim, snap), function.plot)

    # def runSlicePlotFunction(self, function: SlicePlotFunction) -> None:
    #     logging.info("Running {}".format(function.name))
    #     for sim in self.sims:
    #         logging.info("For sim {}".format(sim.name))
    #         for slice_ in sim.getSlices(function.slice_type):
    #             logging.info("For slice {}".format(slice_.name))
    #             function(plt, sim, slice_)
    #             self.saveAndShow(
    #                 "{}_{}_{}".format(sim.name, function.name, slice_.name),
    #             )

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
