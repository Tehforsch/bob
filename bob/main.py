from pathlib import Path
import logging
import argparse

from bob.simulationSet import getSimsFromFolders, SimulationSet
from bob.raxiomSimulation import RaxiomSimulation
from bob.simulation import Simulation
from bob.util import getCommonParentFolder
from bob.plotter import Plotter, PlotFilters, PlotFilter
from bob.postprocess import getFunctionsFromPlotFile, setMatplotlibStyle, runFunctionsWithPlotter, create_pic_folder, generatePlotConfig
from bob.run import runPlotConfig
from bob.report import createReport
import bob.config

from bob.postprocess import readPlotFile


def setupArgs() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Postprocess arepo sims")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-r", "--raxiom", action="store_true", help="Run on raxiom simulations")
    parser.add_argument("--num-threads", type=int, default=20, nargs="?", help="Number of worker threads to use")
    parser.add_argument("--hide", action="store_true", help="Do not show figures in terminal before saving them")
    parser.add_argument("--post", action="store_true", help="Only postprocess the data, do not run the corresponding plot scripts (for cluster)")

    subparsers = parser.add_subparsers(dest="function")

    plotParser = subparsers.add_parser("plot")
    plotParser.add_argument("simFolders", type=Path, nargs="+", help="Path to simulation directories")
    plotParser.add_argument("plot", type=Path, help="The plot configuration")

    replotParser = subparsers.add_parser("replot")
    replotParser.add_argument("simFolders", type=Path, nargs="+", help="Path to simulation directories")
    replotParser.add_argument(
        "--configs", type=Path, nargs="*", help="The plot configurations to replot. Matching plots will be identified by their basename."
    )
    replotParser.add_argument(
        "--only-new",
        dest="onlyNew",
        action="store_true",
        help="Replot all plots that have new data or havent been generated yet but don't refresh old ones",
    )

    generateParser = subparsers.add_parser("generate")
    generateParser.add_argument("plots", type=str, nargs="*", help="The plot configurations to generate")

    runParser = subparsers.add_parser("run")
    runParser.add_argument("plots", type=Path, nargs="*", help="The plot configurations to run")

    reportParser = subparsers.add_parser("report")
    reportParser.add_argument("simFolder", type=Path, nargs="?", help="Path to simulation directory")

    args = parser.parse_args()
    return args


def setupLogging(args: argparse.Namespace) -> None:
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)


def setupAstropy() -> None:
    # Make the parser recognize these
    import astropy.units as pq
    import astropy.cosmology.units as cu

    redshift = pq.def_unit("redshift", cu.redshift)
    littleh = pq.def_unit("littleh", cu.littleh)
    pq.add_enabled_units([redshift, littleh])


def main() -> None:
    args = setupArgs()
    bob.config.numProcesses = args.num_threads
    setupLogging(args)
    setupAstropy()
    simClass = RaxiomSimulation if args.raxiom else Simulation
    if args.function in ["remotePlot", "replot", "plot"] and not args.post:
        setMatplotlibStyle()
    if args.function == "replot":
        for simFolder in args.simFolders:
            plotter = Plotter(simFolder, SimulationSet(simClass, []), args.post, not args.hide)
            if args.configs is not None:
                for config in args.configs:
                    config = readPlotFile(config, safe=True)
                    filters = PlotFilters([PlotFilter(baseName=plotName) for plotName in config])
                    plotter.replot(filters, args.onlyNew, config)
            else:
                plotter.replot(PlotFilters(None), args.onlyNew, None)
    elif args.function == "plot":
        sims = getSimsFromFolders(simClass, args.simFolders)
        parent_folder = getCommonParentFolder(args.simFolders)
        plotter = Plotter(parent_folder, sims, args.post, not args.hide)
        functions = getFunctionsFromPlotFile(args.plot, True)
        create_pic_folder(parent_folder)
        _ = list(runFunctionsWithPlotter(plotter, functions))
    elif args.function == "generate":
        for name in args.plots:
            generatePlotConfig(name)
    elif args.function == "run":
        for name in args.plots:
            runPlotConfig(name)
    elif args.function == "report":
        createReport(Path(".") if args.simFolder is None else args.simFolder)
    else:
        raise ValueError(f"Wrong function type: {args.function}")
