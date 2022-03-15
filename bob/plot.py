from typing import Iterator, List, Optional
import itertools
from pathlib import Path
import argparse
import matplotlib.pyplot as plt
import logging

from bob.postprocessingFunctions import (
    PlotFunction,
    MultiPlotFunction,
    SingleSimPlotFunction,
    SingleSnapshotPlotFunction,
    SingleSnapshotPostprocessingFunction,
    CompareSimSingleSnapshotPlotFunction,
    SlicePlotFunction,
)
from bob.simulationSet import SimulationSet
from bob.snapshot import Snapshot
from bob import config
import bob.plots.ionization
from bob.simulation import Simulation


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
    def __init__(self, parent_folder: Path, sims: SimulationSet, snapshotFilter: List[str], show: bool, quotient_params: Optional[List[str]]) -> None:
        self.pic_folder = parent_folder / config.picFolder
        self.sims = sims
        self.snapshotFilter = snapshotFilter
        self.show = show
        self.quotient_params = quotient_params

    def runPlot(self, function: PlotFunction) -> None:
        logging.info("Running {}".format(function.name))
        function(plt, self.sims)
        self.saveAndShow(function.name)

    def runMultiPlot(self, function: MultiPlotFunction) -> None:
        logging.info("Running {}".format(function.name))
        quotient_params = self.quotient_params
        if quotient_params is None:
            quotient_params = function.default_quotient_params
        print(self.sims.quotient(quotient_params))
        quotient = [sims for (config, sims) in self.sims.quotient(quotient_params)]
        function(plt, quotient)
        self.saveAndShow(function.name)

    def runSingleSimPlot(self, function: SingleSimPlotFunction) -> None:
        logging.info("Running {}".format(function.name))
        for sim in self.sims:
            logging.info("For sim {}".format(sim.name))
            function(plt, sim)
            self.saveAndShow("{}_{}".format(sim.name, function.name))

    def runSingleSnapshotPlot(self, function: SingleSnapshotPlotFunction) -> None:
        logging.info("Running {}".format(function.name))
        for sim in self.sims:
            logging.info("For sim {}".format(sim.name))
            for snap in self.get_snapshots(sim):
                logging.info("For snap {}".format(snap.name))
                function(plt, sim, snap)
                self.saveAndShow(
                    "{}_{}_{}".format(sim.name, function.name, snap.name),
                )

    def runSlicePlotFunction(self, function: SlicePlotFunction) -> None:
        logging.info("Running {}".format(function.name))
        for sim in self.sims:
            logging.info("For sim {}".format(sim.name))
            for slice_ in sim.getSlices():
                logging.info("For slice {}".format(slice_.name))
                function(plt, sim, slice_)
                self.saveAndShow(
                    "{}_{}_{}".format(sim.name, function.name, slice_.name),
                )

    def runCompareSimSingleSnapPlot(
        self,
        function: CompareSimSingleSnapshotPlotFunction,
    ) -> None:
        for (sim1, sim2) in itertools.combinations(self.sims, r=2):
            for (snap1, snap2) in zip(sim1.snapshots, sim2.snapshots):
                assert snap1.time == snap2.time, f"Non-matching snapshots between sims {sim1.name} and {sim2.name}"
                function(plt, sim1, sim2, snap1, snap2)
                self.saveAndShow(function.name)

    def runSingleSnapshotPostprocessingFunction(self, function: SingleSnapshotPostprocessingFunction) -> None:
        logging.info("Running {}".format(function.name))
        for sim in self.sims:
            logging.info("For sim {}".format(sim.name))
            for snap in self.get_snapshots(sim):
                logging.info("For snap {}".format(snap.name))
                function(sim, snap)

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
