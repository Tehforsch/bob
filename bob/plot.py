import itertools
from pathlib import Path
import argparse
import matplotlib.pyplot as plt
import logging

from bob.postprocessingFunctions import PlotFunction, SingleSimPlotFunction, SingleSnapshotPlotFunction, CompareSimSingleSnapshotPlotFunction
from bob.simulationSet import SimulationSet
from bob import config


def runPlot(function: PlotFunction, sims: SimulationSet, args: argparse.Namespace) -> None:
    logging.info("Running {}".format(function.name))
    function(plt, sims)
    saveAndShow(Path(sims.folder, config.picFolder, function.name), args.showFigures)


def runSingleSimPlot(function: SingleSimPlotFunction, sims: SimulationSet, args: argparse.Namespace) -> None:
    logging.info("Running {}".format(function.name))
    for sim in sims:
        logging.info("For sim {}".format(sim.name))
        function(plt, sim)
        simPicFolder = Path(sims.folder, config.picFolder, sim.name)
        saveAndShow(Path(simPicFolder, function.name), args.showFigures)


def runSingleSnapshotPlot(function: SingleSnapshotPlotFunction, sims: SimulationSet, args: argparse.Namespace) -> None:
    logging.info("Running {}".format(function.name))
    for sim in sims:
        logging.info("For sim {}".format(sim.name))
        for snap in sim.snapshots:
            if args.snapshots is None or snap.number in args.snapshots:
                logging.info("For snap {}".format(snap.name))
                simPicFolder = Path(sims.folder, config.picFolder, sim.name)
                saveAndShow(Path(simPicFolder, "{}_{}".format(function.name, snap.name)), args.showFigures)


def runCompareSimSingleSnapPlot(function: CompareSimSingleSnapshotPlotFunction, sims: SimulationSet, args: argparse.Namespace) -> None:
    for (sim1, sim2) in itertools.combinations(sims, r=2):
        for (snap1, snap2) in zip(sim1.snapshots, sim2.snapshots):
            assert snap1.time == snap2.time, f"Non-matching snapshots between sims {sim1.name} and {sim2.name}"
            function(plt, sim1, sim2, snap1, snap2)
            saveAndShow(Path(sims.folder, config.picFolder, function.name), args.showFigures)


def saveAndShow(filename: Path, show: bool) -> None:
    filename.parent.mkdir(exist_ok=True)
    plt.savefig(str(filename) + ".png", dpi=config.dpi)
    if show:
        plt.show()
    plt.clf()
