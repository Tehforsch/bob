from pathlib import Path
import logging
import argparse
from os.path import relpath, realpath

from bob.simulationSet import getSimsFromFolders, SimulationSet
from bob.util import getCommonParentFolder
from bob.watch import watchPost, watchReplot, getPostCommand
from bob.plotter import Plotter, PlotFilters, PlotFilter
from bob.postprocess import getFunctionsFromPlotFile, setMatplotlibStyle, readPlotFile, runFunctionsWithPlotter, create_pic_folder, generatePlotConfig


def setupArgs() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Postprocess arepo sims")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--hide", action="store_true", help="Do not show figures in terminal before saving them")
    parser.add_argument("--post", action="store_true", help="Only postprocess the data, do not run the corresponding plot scripts (for cluster)")

    subparsers = parser.add_subparsers(dest="function")

    plotParser = subparsers.add_parser("plot")
    plotParser.add_argument("simFolders", type=Path, nargs="+", help="Path to simulation directories")
    plotParser.add_argument("plot", type=Path, help="The plot configuration")

    remotePlotParser = subparsers.add_parser("remotePlot")
    remotePlotParser.add_argument("communicationFolder", type=Path, help="The folder to write the new commands to")
    remotePlotParser.add_argument("remoteWorkFolder", type=Path, help="The folder from which the plots should be copied")
    remotePlotParser.add_argument("localWorkFolder", type=Path, help="The folder into which the plots should be copied")
    remotePlotParser.add_argument("simFolders", type=Path, nargs="+", help="Path to simulation directories")
    remotePlotParser.add_argument("plot", type=Path, help="The plot configuration")

    watchReplotParser = subparsers.add_parser("watchReplot")
    watchReplotParser.add_argument("communicationFolder", type=Path, help="The folder to write the new commands to")
    watchReplotParser.add_argument("remoteWorkFolder", type=Path, help="The folder from which the plots should be copied")
    watchReplotParser.add_argument("localWorkFolder", type=Path, help="The folder into which the plots should be copied")
    watchReplotParser.add_argument("simFolders", type=Path, nargs="+", help="Path to simulation directories")

    replotParser = subparsers.add_parser("replot")
    replotParser.add_argument("simFolders", type=Path, nargs="+", help="Path to simulation directories")
    replotParser.add_argument("--plots", type=str, nargs="*", help="The plots to replot")
    replotParser.add_argument("--config", type=Path, help="A custom plot config to overwrite the one created during postprocessing")
    replotParser.add_argument(
        "--only-new",
        dest="onlyNew",
        action="store_true",
        help="Replot all plots that have new data or havent been generated yet but don't refresh old ones",
    )

    watchPostParser = subparsers.add_parser("watchPost")
    watchPostParser.add_argument("communicationFolder", type=Path, help="The folder to watch for new commands")
    watchPostParser.add_argument("workFolder", type=Path, help="The work folder to execute the commands in")

    generateParser = subparsers.add_parser("generate")
    generateParser.add_argument("plot", type=str, help="The name of the plot configuration")

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
    setupLogging(args)
    setupAstropy()
    if args.function in ["remotePlot", "replot", "plot"] and not args.post:
        setMatplotlibStyle()
    if args.function == "watchPost":
        watchPost(args.communicationFolder, args.workFolder)
    elif args.function == "remotePlot":
        if len(args.simFolders) > 1:
            raise NotImplementedError("No implementation for multiple sim folders currently (easy extension)")
        config = readPlotFile(args.plot, False)
        relPath = Path(relpath(realpath(args.simFolders[0]), realpath(args.localWorkFolder)))
        command = getPostCommand(relPath, config)
        command.write(args.communicationFolder)
        watchReplot(args.communicationFolder, args.remoteWorkFolder, args.simFolders[0], command["id"], not args.hide)
    elif args.function == "watchReplot":
        watchReplot(args.communicationFolder, args.remoteWorkFolder, args.simFolders[0], None, not args.hide)
    elif args.function == "replot":
        for simFolder in args.simFolders:
            plotter = Plotter(simFolder, SimulationSet([]), args.post, not args.hide)
            filters = PlotFilters(None if args.plots is None else [PlotFilter(baseName=plot) for plot in args.plots])
            plotter.replot(filters, args.onlyNew, args.config)
    elif args.function == "plot":
        sims = getSimsFromFolders(args.simFolders)
        parent_folder = getCommonParentFolder(args.simFolders)
        plotter = Plotter(parent_folder, sims, args.post, not args.hide)
        functions = getFunctionsFromPlotFile(args.plot, True)
        create_pic_folder(parent_folder)
        _ = list(runFunctionsWithPlotter(plotter, functions))
    elif args.function == "generate":
        name = args.plot
        generatePlotConfig(name)
    else:
        raise ValueError(f"Wrong function type: {args.function}")
