from pathlib import Path
import argparse
import matplotlib.pyplot as plt
import logging

from bob.postprocessingFunctions import PlotFunction, SingleSimPlotFunction, SingleSnapshotPlotFunction
from bob.simulationSet import SimulationSet
from bob import config


def runPlot(function: PlotFunction, sims: SimulationSet, args: argparse.Namespace) -> None:
    logging.info("Running {}".format(function.name))
    function(plt, sims)
    plt.savefig(Path(sims.folder, config.picFolder, function.name), dpi=config.dpi)
    if args.showFigures:
        plt.show()


def runSingleSimPlot(function: SingleSimPlotFunction, sims: SimulationSet, args: argparse.Namespace) -> None:
    logging.info("Running {}".format(function.name))
    for sim in sims:
        logging.info("For sim {}".format(sim.name))
        function(plt, sim)
        simPicFolder = Path(sims.folder, config.picFolder, sim.name)
        simPicFolder.mkdir(exist_ok=True)
        plt.savefig(Path(simPicFolder, function.name), dpi=config.dpi)
        if args.showFigures:
            plt.show()


def runSingleSnapshotPlot(function: SingleSnapshotPlotFunction, sims: SimulationSet, args: argparse.Namespace) -> None:
    logging.info("Running {}".format(function.name))
    for sim in sims:
        logging.info("For sim {}".format(sim.name))
        for snap in sim.snapshots:
            logging.info("For snap {}".format(snap.name))
            function(plt, snap)
            simPicFolder = Path(sims.folder, config.picFolder, sim.name)
            simPicFolder.mkdir(exist_ok=True)
            plt.savefig(Path(simPicFolder, "{}_{}".format(function.name, snap.name)), dpi=config.dpi)
            if args.showFigures:
                plt.show()
