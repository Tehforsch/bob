from pathlib import Path
import matplotlib.pyplot as plt
from abc import abstractmethod
from typing import Callable, Any, List, Optional
from bob.simulation import Simulation
from bob.simulationSet import SimulationSet
from bob.snapshot import Snapshot


class PostprocessingFunction:
    def __init__(self, f: Callable[..., Any], name: str) -> None:
        self.f = f
        self.name = name


class SingleSnapshotPostprocessingFunction(PostprocessingFunction):
    def __call__(self, sim: Simulation, snap: Snapshot) -> None:
        return self.f(sim, snap)


class PlotFunction(PostprocessingFunction):
    def __call__(self, axes: plt.axes, sims: SimulationSet) -> None:
        return self.f(axes, sims)


class MultiPlotFunction(PostprocessingFunction):
    def __init__(self, f: Callable[..., Any], name: str) -> None:
        super().__init__(f, name)
        self.default_quotient_params: List[str] = []

    def __call__(self, axes: plt.axes, sims: List[SimulationSet]) -> None:
        return self.f(axes, sims)


class SingleSimPlotFunction(PostprocessingFunction):
    def __call__(self, sim: Simulation, snap: Snapshot) -> None:
        return self.f(sim, snap)


class SingleSnapshotPlotFunction(PostprocessingFunction):
    def __call__(self, axes: plt.axes, sim: Simulation, snap: Snapshot) -> None:
        return self.f(axes, sim, snap)


class CompareSimSingleSnapshotPlotFunction(PostprocessingFunction):
    def __call__(self, axes: plt.axes, sim1: Simulation, sim2: Simulation, snap1: Snapshot, snap2: Snapshot) -> None:
        return self.f(axes, sim1, sim2, snap1, snap2)


class SlicePlotFunction(PostprocessingFunction):
    def __call__(self, axes: plt.axes, sim: Simulation, slice_: Any) -> None:
        return self.f(axes, sim, slice_)


# Giving up on mypy hints on this one
def addToList(name: Optional[str], cls: Any, modify: Optional[Callable[..., Any]] = None) -> Callable[[Callable[..., Any]], Any]:
    def wrapper(f: Callable[..., Any]) -> Any:
        if name is None:
            newF = cls(f, f.__name__)
        else:
            newF = cls(f, name)
        if modify is not None:
            modify(newF)
        postprocessingFunctions.append(newF)
        return newF

    return wrapper


def addSingleSnapshotPostprocessing(
    name: Optional[str],
) -> Callable[[Callable[..., Any]], SingleSnapshotPostprocessingFunction]:
    return addToList(name, SingleSnapshotPostprocessingFunction)


def addPlot(name: Optional[str]) -> Callable[[Callable[..., Any]], PlotFunction]:
    return addToList(name, PlotFunction)


def addMultiPlot(name: Optional[str], default_quotient_params: List[str] = []) -> Callable[[Callable[..., Any]], MultiPlotFunction]:
    def modify(f: MultiPlotFunction) -> None:
        f.default_quotient_params = default_quotient_params

    return addToList(name, MultiPlotFunction, modify)


def addSingleSimPlot(
    name: Optional[str],
) -> Callable[[Callable[..., Any]], SingleSimPlotFunction]:
    return addToList(name, SingleSimPlotFunction)


def addSingleSnapshotPlot(
    name: Optional[str],
) -> Callable[[Callable[..., Any]], SingleSnapshotPlotFunction]:
    return addToList(name, SingleSnapshotPlotFunction)


def addSlicePlot(
    name: Optional[str],
) -> Callable[[Callable[..., Any]], SlicePlotFunction]:
    return addToList(name, SlicePlotFunction)


def addCompareSimSingleSnapshotPlot(
    name: Optional[str],
) -> Callable[[Callable[..., Any]], CompareSimSingleSnapshotPlotFunction]:
    return addToList(name, CompareSimSingleSnapshotPlotFunction)


def checkNoDoubledNames() -> None:
    functionNames: List[str] = [f.name for f in postprocessingFunctions]
    assert len(set(functionNames)) == len(functionNames), "Two functions with the same name in postprocessing functions!"


postprocessingFunctions: List[PostprocessingFunction] = []


def functionNames() -> List[str]:
    return [f.name for f in postprocessingFunctions]
