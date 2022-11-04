import itertools

import astropy.units as pq
import matplotlib.pyplot as plt

from abc import ABC, abstractmethod
from typing import Any, Tuple, Iterable, Dict
from bob.simulation import Simulation
from bob.simulationSet import SimulationSet
from bob.snapshot import Snapshot
from bob.result import Result
from bob.multiSet import MultiSet
from bob.plotConfig import PlotConfig


def fillInUnit(label: str, unit: str) -> str:
    if "UNIT" in label:
        return label.replace("UNIT", str(unit).replace("littleh", "h").replace("**", "^").replace("*", "\\cdot"))
    else:
        return label


class PostprocessingFunction(ABC):
    name = ""

    def __init__(self, config: PlotConfig) -> None:
        self.config = config
        self.config.setDefault("sims", None)
        self.config.setDefault("outputFileType", "png")
        self.config.setDefault("name", self.name)

    def getName(self, **kwargs: Any) -> str:
        combined = self.config.copy()
        combined.update(kwargs)
        if "snap" in kwargs and "sim" in kwargs:
            snap: Snapshot = kwargs["snap"]
            sim: Simulation = kwargs["sim"]
            if sim.simType().can_get_redshift():
                combined["redshift"] = snap.timeQuantity("z")
        return self.config["name"].format(**combined)

    def setupLinePlot(self, ax: Any = None) -> None:
        self.setupLabels()
        if ax is None:
            ax = plt
        if "xLim" in self.config:
            plt.xlim(*self.config["xLim"])
        if "yLim" in self.config:
            plt.ylim(*self.config["yLim"])

    def setupLabels(self) -> None:
        plt.xlabel(fillInUnit(self.config["xLabel"], str(self.config["xUnit"])))
        plt.ylabel(fillInUnit(self.config["yLabel"], str(self.config["yUnit"])))

    def addLine(self, xQuantity: pq.Quantity, yQuantity: pq.Quantity, *args: Any, **kwargs: Any) -> None:
        xUnit = pq.Unit(self.config["xUnit"])
        yUnit = pq.Unit(self.config["yUnit"])
        plt.plot(xQuantity.to(xUnit).value, yQuantity.to(yUnit).value, *args, **kwargs)

    def histogram(self, xQuantity: pq.Quantity, yQuantity: pq.Quantity, *args: Any, **kwargs: Any) -> None:
        xUnit = pq.Unit(self.config["xUnit"])
        yUnit = pq.Unit(self.config["yUnit"])
        plt.hist2d(xQuantity.to(xUnit).value, yQuantity.to(yUnit).value, *args, **kwargs)

    def image(
        self, ax: plt.Axes, image: pq.Quantity, extent: Tuple[pq.Quantity, pq.Quantity, pq.Quantity, pq.Quantity], *args: Any, **kwargs: Any
    ) -> None:
        xUnit = pq.Unit(self.config["xUnit"])
        yUnit = pq.Unit(self.config["yUnit"])
        extent = (extent[0].to_value(xUnit), extent[1].to_value(xUnit), extent[2].to_value(yUnit), extent[3].to_value(yUnit))
        vUnit = pq.Unit(self.config["vUnit"])
        image = ax.imshow(image.to(vUnit).value, extent=extent, *args, **kwargs)
        cbar = plt.colorbar(image)
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
        self.config.setDefault("name", self.name + "_{simName}_{snapName}")
        self.config.setDefault("showTime", True)
        self.config.setDefault("time", "t")
        self.config.setDefault("timeUnit", pq.Myr)

    def showTime(self, fig: plt.Figure, result: Result) -> None:
        if self.config["time"] == "t":
            time = result.time.to(self.config["timeUnit"]).value
            timeUnit = str(self.config["timeUnit"])
            fig.suptitle(f"Time: {time:.01f} {timeUnit}", fontsize=12)
        else:
            fig.suptitle(f"Redshift: {result.time:.01f}", fontsize=12)

    def post(self, sim: Simulation, snap: Snapshot) -> Result:
        result = Result()
        result.time = snap.timeQuantity(self.config["time"])
        return result

    def showTimeIfDesired(self, fig: plt.Figure, result: Result) -> None:
        if self.config["showTime"]:
            self.showTime(fig, result)


class SetFn(PostprocessingFunction):
    def __init__(self, config: PlotConfig) -> None:
        super().__init__(config)
        self.config.setDefault("labels", None)
        self.config.setDefault("quotient", "single")
        self.config.setDefault("name", self.name + "_{setNum}")

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
        self.config.setDefault("quotient", "single")
        self.config.setDefault("colors", None)
        self.config.setDefault("styles", None)

    @abstractmethod
    def post(self, sims: MultiSet) -> Result:
        pass

    @abstractmethod
    def plot(self, axes: plt.axes, result: Result) -> None:
        pass

    def getColors(self) -> Iterable[str]:
        if self.config["colors"] is None:
            return ["b", "r", "g", "purple", "brown", "orange", "pink", "teal"] * 5
        else:
            return self.config["colors"]

    def getLabels(self) -> Iterable[str]:
        labels = self.config["labels"]
        if labels is None:
            labels = []
        return itertools.chain(labels, itertools.repeat(""))

    def getStyles(self) -> Iterable[Dict]:
        if self.config["styles"] is None:
            return [{}] * 20
        else:
            return self.config["styles"]


class SliceFn(PostprocessingFunction):
    def __init__(self, config: PlotConfig) -> None:
        super().__init__(config)
        self.config.setRequired("field")
        self.config.setDefault("snapshots", None)
        self.config.setDefault("name", self.name + "_{sliceName}_{simName}")

    @abstractmethod
    def post(self, sim: Simulation, slice_: Any) -> Result:
        pass

    @abstractmethod
    def plot(self, axes: plt.axes, result: Result) -> None:
        pass
