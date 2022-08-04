import argparse
import itertools

import astropy.units as pq
import matplotlib.pyplot as plt

from abc import ABC, abstractmethod
from typing import Any, List, Tuple, Iterable
from bob.simulation import Simulation
from bob.simulationSet import SimulationSet
from bob.snapshot import Snapshot
from bob.result import Result
from bob.multiSet import MultiSet
from bob.plotConfig import PlotConfig


class PostprocessingFunction(ABC):
    name = ""

    def init(self, args: argparse.Namespace) -> None:
        self.config: PlotConfig = PlotConfig({})

    def setArgs(self) -> None:
        pass

    def getName(self, args: argparse.Namespace) -> str:
        return self.name

    def setPlotConfig(self, plotConfig: PlotConfig) -> None:
        self.config = plotConfig

    def setupLinePlot(self) -> None:
        self.setupLabels()
        if "xLim" in self.config:
            plt.xlim(*self.config["xLim"])
        if "yLim" in self.config:
            plt.ylim(*self.config["yLim"])

    def setupLabels(self) -> None:
        plt.xlabel(self.config["xLabel"])
        plt.ylabel(self.config["yLabel"])

    def addLine(self, xQuantity: pq.Quantity, yQuantity: pq.Quantity, *args: Any, **kwargs: Any) -> None:
        xUnit = pq.Unit(self.config["xUnit"])
        yUnit = pq.Unit(self.config["yUnit"])
        plt.plot(xQuantity.to(xUnit).value, yQuantity.to(yUnit).value, *args, **kwargs)

    def histogram(self, xQuantity: pq.Quantity, yQuantity: pq.Quantity, *args: Any, **kwargs: Any) -> None:
        xUnit = pq.Unit(self.config["xUnit"])
        yUnit = pq.Unit(self.config["yUnit"])
        plt.hist2d(xQuantity.to(xUnit).value, yQuantity.to(yUnit).value, *args, **kwargs)

    def image(self, image: pq.Quantity, extent: Tuple[pq.Quantity, pq.Quantity, pq.Quantity, pq.Quantity], *args: Any, **kwargs: Any) -> None:
        xUnit = pq.Unit(self.config["xUnit"])
        yUnit = pq.Unit(self.config["yUnit"])
        extent = (extent[0].to_value(xUnit), extent[1].to_value(xUnit), extent[2].to_value(yUnit), extent[3].to_value(yUnit))
        vUnit = pq.Unit(self.config["vUnit"])
        plt.imshow(image.to(vUnit).value, extent=extent, *args, **kwargs)
        cbar = plt.colorbar()
        cbar.set_label(self.config["cLabel"])

    def scatter(self, xdata: pq.Quantity, ydata: pq.Quantity, *args: Any, **kwargs: Any) -> None:
        xUnit = pq.Unit(self.config["xUnit"])
        yUnit = pq.Unit(self.config["yUnit"])
        plt.scatter(xdata.to_value(xUnit), ydata.to_value(yUnit), *args, **kwargs)


class SnapFn(PostprocessingFunction):
    @abstractmethod
    def post(self, args: argparse.Namespace, sim: Simulation, snap: Snapshot) -> Result:
        pass

    @abstractmethod
    def plot(self, axes: plt.axes, result: Result) -> None:
        pass


class SetFn(PostprocessingFunction):
    @abstractmethod
    def post(self, args: argparse.Namespace, sims: SimulationSet) -> Result:
        pass

    @abstractmethod
    def plot(self, axes: plt.axes, result: Result) -> None:
        pass

    def setArgs(self) -> None:
        self.config.setDefault("labels", None)


class MultiSetFn(PostprocessingFunction):
    @abstractmethod
    def post(self, args: argparse.Namespace, sims: MultiSet) -> Result:
        pass

    @abstractmethod
    def plot(self, axes: plt.axes, result: Result) -> None:
        pass

    def setArgs(self) -> None:
        self.config.setDefault("labels", None)

    def getColors(self) -> Iterable[str]:
        return itertools.cycle(["b", "r", "g", "purple", "brown", "orange"])

    def getLabels(self) -> Iterable[str]:
        self.config.setDefault("labels", [])
        return itertools.chain(self.config["labels"], itertools.cycle(""))


class SliceFn(PostprocessingFunction):
    def init(self, args: argparse.Namespace) -> None:
        self.slice_field = args.slice_field

    def setArgs(self) -> None:
        self.config.setRequired("field")

    def getName(self, args: argparse.Namespace) -> str:
        return f"{self.name}_{args.slice_field}"

    @abstractmethod
    def post(self, args: argparse.Namespace, sim: Simulation, slice_: Any) -> Result:
        pass

    @abstractmethod
    def plot(self, axes: plt.axes, result: Result) -> None:
        pass


def addToList(name: str, fn: PostprocessingFunction) -> Any:
    fn.name = name
    postprocessingFunctions.append(fn)


postprocessingFunctions: List[PostprocessingFunction] = []
