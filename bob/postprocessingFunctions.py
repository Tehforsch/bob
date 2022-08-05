import itertools

import astropy.units as pq
import matplotlib.pyplot as plt

from abc import ABC, abstractmethod
from typing import Any, List, Tuple, Iterable, Type
from bob.simulation import Simulation
from bob.simulationSet import SimulationSet
from bob.snapshot import Snapshot
from bob.result import Result
from bob.multiSet import MultiSet
from bob.plotConfig import PlotConfig


class PostprocessingFunction(ABC):
    name = ""

    def __init__(self, config: PlotConfig) -> None:
        self.config = config
        self.config.setDefault("sims", None)

    def getName(self) -> str:
        return self.name

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

    def __repr__(self) -> str:
        return f"{self.name}: {self.config}"

    @abstractmethod
    def plot(self, axes: plt.axes, result: Result) -> None:
        pass


class SnapFn(PostprocessingFunction):
    def __init__(self, config: PlotConfig) -> None:
        super().__init__(config)
        self.config.setDefault("snapshots", None)

    @abstractmethod
    def post(self, sim: Simulation, snap: Snapshot) -> Result:
        pass

    @abstractmethod
    def plot(self, axes: plt.axes, result: Result) -> None:
        pass


class SetFn(PostprocessingFunction):
    def __init__(self, config: PlotConfig) -> None:
        super().__init__(config)
        self.config.setDefault("labels", None)

    @abstractmethod
    def post(self, sims: SimulationSet) -> Result:
        pass

    @abstractmethod
    def plot(self, axes: plt.axes, result: Result) -> None:
        pass


class MultiSetFn(PostprocessingFunction):
    def __init__(self, config: PlotConfig) -> None:
        super().__init__(config)
        self.config.setDefault("labels", None)

    @abstractmethod
    def post(self, sims: MultiSet) -> Result:
        pass

    @abstractmethod
    def plot(self, axes: plt.axes, result: Result) -> None:
        pass

    def getColors(self) -> Iterable[str]:
        return itertools.cycle(["b", "r", "g", "purple", "brown", "orange"])

    def getLabels(self) -> Iterable[str]:
        labels = self.config["labels"]
        if labels is None:
            labels = []
        return itertools.chain(labels, itertools.cycle(""))


class SliceFn(PostprocessingFunction):
    def __init__(self, config: PlotConfig) -> None:
        super().__init__(config)
        self.config.setRequired("field")
        self.config.setDefault("snapshots", None)

    def getName(self) -> str:
        field = self.config["field"]
        return f"{self.name}_{field}"

    @abstractmethod
    def post(self, sim: Simulation, slice_: Any) -> Result:
        pass

    @abstractmethod
    def plot(self, axes: plt.axes, result: Result) -> None:
        pass


def addToList(name: str, fn: Type[PostprocessingFunction]) -> Any:
    fn.name = name
    postprocessingFunctions.append(fn)


postprocessingFunctions: List[Type[PostprocessingFunction]] = []
