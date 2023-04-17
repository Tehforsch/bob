import os
import yaml
from typing import Iterator, List, Optional, Callable, Union, Tuple, Any
from pathlib import Path
import matplotlib.pyplot as plt
import logging
import astropy.units as pq

from bob.postprocessingFunctions import (
    SetFn,
    MultiSetFn,
    SnapFn,
    SliceFn,
)
from bob.simulationSet import SimulationSet, Single
import bob.config
from bob.result import Result
from bob.postprocessingFunctions import PostprocessingFunction
from bob.multiSet import MultiSet
from bob.pool import runInPool
from bob.util import zeroPadToLength, showImageInTerminal, walkfiles, getFolderNames
from bob.snapshotFilter import SnapshotFilter

QuotientParams = Optional[Union[List[str], Single]]


def transformReadable(item: Tuple[str, Any]) -> Tuple[str, Any]:
    (k, v) = item
    if type(v) == pq.Quantity:
        return (k, str(v))
    return (k, v)


class PlotName:
    def __init__(self, picFolder: Path, baseName: str, qualifiedName: str) -> None:
        self.picFolder = picFolder
        self.baseName = baseName
        self.qualifiedName = qualifiedName
        self.subName = qualifiedName.replace("{}_".format(baseName), "")

    def folder(self) -> Path:
        return self.picFolder / self.baseName

    def dataFolder(self) -> Path:
        return self.folder() / self.subName

    def getOutputFile(self, outputFileType: str) -> Path:
        return self.folder() / "{}.{}".format(self.qualifiedName, outputFileType)

    def withPicFolder(self, picFolder: Path) -> "PlotName":
        return PlotName(picFolder, self.baseName, self.qualifiedName)

    def __repr__(self) -> str:
        return "{} {} {} {}".format(self.picFolder, self.baseName, self.qualifiedName, self.subName)


class PlotFilter:
    def __init__(self, baseName: Optional[str] = None, qualifiedName: Optional[str] = None) -> None:
        self.baseName = baseName
        self.qualifiedName = qualifiedName

    def contains(self, plot: PlotName) -> bool:
        if self.baseName is not None and plot.baseName == self.baseName:
            return True
        if self.qualifiedName is not None and plot.qualifiedName == self.qualifiedName:
            return True
        return False


class PlotFilters:
    def __init__(self, filters: Optional[List[PlotFilter]]) -> None:
        self.filters = filters

    def contains(self, plot: PlotName) -> bool:
        if self.filters is None:
            return True
        else:
            return any(f.contains(plot) for f in self.filters)


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
        self.postprocess_only = postprocess_only
        self.show = show

    def filterSims(self, select: Optional[List[str]]) -> SimulationSet:
        if select is None:
            return self.sims
        else:
            select = [str(x) for x in select]
            return SimulationSet(self.sims.sim_type, (sim for sim in self.sims if sim.name in select))

    def isNew(self, plot: PlotName, fileType: str) -> bool:
        imageFile = plot.getOutputFile(fileType)
        if not imageFile.is_file():
            return True
        else:
            mtimeData = max(os.path.getmtime(str(f)) for f in walkfiles(plot.dataFolder()))
            mtimeImage = os.path.getmtime(imageFile)
            return mtimeImage < mtimeData

    def testAllSuffixes(self, name: PlotName) -> Optional[str]:
        for suffix in bob.config.possibleImageSuffixes:
            if name.getOutputFile(suffix).is_file():
                return suffix
        return None

    def getNewPlots(self) -> Iterator[PlotName]:
        basenames = getFolderNames(self.picFolder)
        for baseName in basenames:
            for qualifiedName in getFolderNames(self.picFolder / baseName):
                name = PlotName(self.picFolder, baseName, qualifiedName)
                suffix = self.testAllSuffixes(name)
                if suffix is None or self.isNew(name, suffix):
                    yield name

    def replot(self, plotFilters: PlotFilters, onlyNew: bool, customConfig: Optional[dict]) -> None:
        if onlyNew:
            plots = list(self.getNewPlots())
        else:
            plotBaseNames = getFolderNames(self.picFolder)
            plots = [
                PlotName(self.picFolder, baseName, qualifiedName)
                for baseName in plotBaseNames
                for qualifiedName in getFolderNames(self.picFolder / baseName)
            ]
        if customConfig is not None:
            config = customConfig
        else:
            config = None
        plots.sort(key=lambda plot: plot.qualifiedName)
        plots = [plot for plot in plots if plotFilters.contains(plot)]
        for path in runInPool(runPlot, plots, self, config):
            if self.show:
                showImageInTerminal(path)

    def runPostAndPlot(
        self, fn: PostprocessingFunction, qualifiedName: str, post: Callable[[], Result], plot: Callable[[plt.axes, Result], None]
    ) -> PlotName:
        name = PlotName(self.picFolder, fn.name, qualifiedName)
        logging.info("Running {}".format(name.qualifiedName))
        result = post()
        self.save(fn, name, result)
        if not self.postprocess_only:
            plot(plt, result)
            path = self.saveAndShow(name, fn)
            if self.show:
                showImageInTerminal(path)
        return name

    def save(self, fn: PostprocessingFunction, name: PlotName, result: Result) -> None:
        plotDataFolder = name.dataFolder()
        plotDataFolder.mkdir(parents=True, exist_ok=True)
        self.savePlotInfo(fn, plotDataFolder)
        self.saveResult(result, plotDataFolder)

    def savePlotInfo(self, fn: PostprocessingFunction, plotDataFolder: Path) -> None:
        filename = plotDataFolder / bob.config.plotSerializationFileName
        yaml.dump({fn.name: dict(transformReadable(item) for item in fn.config.items())}, open(filename, "w"))

    def saveResult(self, result: Result, plotDataFolder: Path) -> None:
        result.save(plotDataFolder)

    def getQuotient(
        self, quotient_params: Optional[Union[str, List[str]]], sims_filter: Optional[List[str]], labels: Optional[List[str]]
    ) -> MultiSet:
        if type(quotient_params) == str and quotient_params.lower() == "single":
            params: Union[Single, List[str]] = Single()
        elif quotient_params is None:
            params = []
        elif type(quotient_params) == list:
            params = quotient_params
        else:
            raise NotImplementedError(f"Type: {type(quotient_params)}")
        sims = self.filterSims(sims_filter)
        return MultiSet(sims.quotient(params), labels)

    def runMultiSetFn(self, function: MultiSetFn) -> Iterator[PlotName]:
        quotient = self.getQuotient(function.config["quotient"], function.config["sims"], function.config["labels"])
        function.updateLabelsInConfig(quotient)
        yield self.runPostAndPlot(function, function.getName(), lambda: function.post(quotient), function.plot)

    def runSetFn(self, function: SetFn) -> Iterator[PlotName]:
        quotient = self.getQuotient(function.config["quotient"], function.config["sims"], function.config["labels"])
        numSims = len(quotient)
        for i, (config, sims) in enumerate(quotient.iterWithConfigs()):
            yield self.runPostAndPlot(function, function.getName(setNum=zeroPadToLength(i, numSims)), lambda: function.post(sims), function.plot)

    def runSnapFn(self, function: SnapFn) -> Iterator[PlotName]:
        sims = self.filterSims(function.config["sims"])
        for sim in sims:
            snapshots = SnapshotFilter(function.config["snapshots"]).get_snapshots(sim)
            for snap in snapshots:
                simName = zeroPadToLength(int(sim.name), len(sims))
                snapName = zeroPadToLength(int(snap.name), len(snapshots))
                qualifiedName = function.getName(sim=sim, snap=snap, simName=simName, snapName=snapName)
                yield self.runPostAndPlot(function, qualifiedName, lambda: function.post(sim, snap), function.plot)

    def runSliceFn(self, function: SliceFn) -> Iterator[PlotName]:
        sims = self.filterSims(function.config["sims"])
        for sim in sims:
            for slice_ in sim.getSlices(function.config["field"]):
                if function.config["snapshots"] is None or any(str(arg_snap) == slice_.name for arg_snap in function.config["snapshots"]):
                    simName = zeroPadToLength(int(sim.name), len(sims))
                    qualifiedName = function.getName(simName=simName, sliceName=slice_.name)
                    yield self.runPostAndPlot(function, qualifiedName, lambda: function.post(sim, slice_), function.plot)

    def saveAndShow(self, name: PlotName, fn: PostprocessingFunction) -> Path:
        filepath = name.getOutputFile(fn.config["outputFileType"])
        filepath.parent.mkdir(exist_ok=True)
        plt.savefig(str(filepath), dpi=bob.config.dpi)
        plt.clf()
        return filepath


def getBaseName(plotName: str) -> str:
    if "_" not in plotName:
        return plotName
    return plotName[: plotName.index("_")]


# Needs to be a top-level function so it can be used by multiprocessing
def runPlot(plotter: Plotter, customConfig: Optional[dict], plot: PlotName) -> Path:
    from bob.postprocess import getFunctionsFromPlotFile, getFunctionsFromPlotConfigs

    logging.info(f"Replotting {plot.qualifiedName}")
    dataFolder = plot.dataFolder()
    if customConfig is not None:
        functions = getFunctionsFromPlotConfigs(customConfig)
    else:
        functions = getFunctionsFromPlotFile(dataFolder / bob.config.plotSerializationFileName, False)
    assert len(functions) == 1, "More than one plot in replot information."
    fn = functions[0]
    result = Result.readFromFolder(dataFolder)
    fn.plot(plt, result)
    return plotter.saveAndShow(plot, fn)
