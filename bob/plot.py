import itertools
from pathlib import Path
import argparse
import matplotlib.pyplot as plt
import logging

from bob.postprocessingFunctions import (
    PlotFunction,
    SingleSimPlotFunction,
    SingleSnapshotPlotFunction,
    SingleSnapshotPostprocessingFunction,
    CompareSimSingleSnapshotPlotFunction,
)
from bob.simulationSet import SimulationSet
from bob.snapshot import Snapshot
from bob import config


def isInSnapshotArgs(snap: Snapshot, args: argparse.Namespace) -> bool:
    return args.snapshots is None or any(isSameSnapshot(arg_snap, snap) for arg_snap in args.snapshots)


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


def runPlot(function: PlotFunction, sims: SimulationSet, args: argparse.Namespace) -> None:
    logging.info("Running {}".format(function.name))
    function(plt, sims)
    saveAndShow(Path(sims.folder, config.picFolder, function.name), args.show)


def runSingleSimPlot(function: SingleSimPlotFunction, sims: SimulationSet, args: argparse.Namespace) -> None:
    logging.info("Running {}".format(function.name))
    for sim in sims:
        logging.info("For sim {}".format(sim.name))
        function(plt, sim)
        simPicFolder = Path(sims.folder, config.picFolder, sim.name)
        saveAndShow(Path(simPicFolder, function.name), args.show)


def runSingleSnapshotPlot(function: SingleSnapshotPlotFunction, sims: SimulationSet, args: argparse.Namespace) -> None:
    logging.info("Running {}".format(function.name))
    for sim in sims:
        logging.info("For sim {}".format(sim.name))
        for snap in sim.snapshots:
            if isInSnapshotArgs(snap, args):
                logging.info("For snap {}".format(snap.name))
                function(plt, sim, snap)
                simPicFolder = Path(sims.folder, config.picFolder, sim.name)
                saveAndShow(
                    Path(simPicFolder, "{}_{}".format(function.name, snap.name)),
                    args.show,
                )


def runCompareSimSingleSnapPlot(
    function: CompareSimSingleSnapshotPlotFunction,
    sims: SimulationSet,
    args: argparse.Namespace,
) -> None:
    for (sim1, sim2) in itertools.combinations(sims, r=2):
        for (snap1, snap2) in zip(sim1.snapshots, sim2.snapshots):
            assert snap1.time == snap2.time, f"Non-matching snapshots between sims {sim1.name} and {sim2.name}"
            function(plt, sim1, sim2, snap1, snap2)
            saveAndShow(Path(sims.folder, config.picFolder, function.name), args.show)


def runSingleSnapshotPostprocessingFunction(function: SingleSnapshotPostprocessingFunction, sims: SimulationSet, args: argparse.Namespace) -> None:
    logging.info("Running {}".format(function.name))
    for sim in sims:
        logging.info("For sim {}".format(sim.name))
        for snap in sim.snapshots:
            if isInSnapshotArgs(snap, args):
                logging.info("For snap {}".format(snap.name))
                function(sim, snap)


def saveAndShow(filename: Path, show: bool) -> None:
    filename.parent.mkdir(exist_ok=True)
    plt.savefig(str(filename) + ".png", dpi=config.dpi)
    if show:
        plt.show()
    plt.clf()
