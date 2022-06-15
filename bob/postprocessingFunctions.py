import argparse

import astropy.units as pq
import matplotlib.pyplot as plt

from abc import ABC, abstractmethod
from typing import Any, List
from bob.simulation import Simulation
from bob.simulationSet import SimulationSet
from bob.snapshot import Snapshot
from bob.result import Result
from bob.multiSet import MultiSet
from bob.style import Style


class PostprocessingFunction(ABC):
    name = ""

    def init(self, args: argparse.Namespace) -> None:
        self.style: Style = Style({})

    def setArgs(self, subparser: argparse.ArgumentParser) -> None:
        pass

    def getName(self, args: argparse.Namespace) -> str:
        return self.name

    def setStyle(self, style: Style) -> None:
        self.style = style

    def setupLinePlot(self) -> None:
        self.setupLabels()
        if "xLim" in self.style:
            plt.xlim(*self.style["xLim"])
        if "yLim" in self.style:
            plt.ylim(*self.style["yLim"])

    def setupLabels(self) -> None:
        plt.xlabel(self.style["xLabel"])
        plt.ylabel(self.style["yLabel"])

    def addLine(self, xQuantity: pq.Quantity, yQuantity: pq.Quantity, *args: Any, **kwargs: Any) -> None:
        xUnit = pq.Unit(self.style["xUnit"])
        yUnit = pq.Unit(self.style["yUnit"])
        plt.plot(xQuantity.to(xUnit).value, yQuantity.to(yUnit).value, *args, **kwargs)

    def histogram(self, xQuantity: pq.Quantity, yQuantity: pq.Quantity, *args: Any, **kwargs: Any) -> None:
        xUnit = pq.Unit(self.style["xUnit"])
        yUnit = pq.Unit(self.style["yUnit"])
        plt.hist2d(xQuantity.to(xUnit).value, yQuantity.to(yUnit).value, *args, **kwargs)

    def image(self, image: pq.Quantity, *args: Any, **kwargs: Any) -> None:
        vUnit = pq.Unit(self.style["vUnit"])
        plt.imshow(image.to(vUnit).value, *args, **kwargs)


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

    def setArgs(self, subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument("--labels", nargs="*", type=str)


class MultiSetFn(PostprocessingFunction):
    @abstractmethod
    def post(self, args: argparse.Namespace, sims: MultiSet) -> Result:
        pass

    @abstractmethod
    def plot(self, axes: plt.axes, result: Result) -> None:
        pass

    def setArgs(self, subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument("--labels", nargs="*", type=str)


class SliceFn(PostprocessingFunction):
    def init(self, args: argparse.Namespace) -> None:
        self.slice_field = args.slice_field

    def setArgs(self, subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument("--slice_field", choices=["xHP", "temp", "density"], required=True)

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
