import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from abc import ABC, abstractmethod
from typing import Callable, Any, List, Optional
from bob.simulation import Simulation
from bob.simulationSet import SimulationSet
from bob.snapshot import Snapshot
from bob.result import Result


class PostprocessingFunction(ABC):
    def setArgs(self, subparser: argparse.ArgumentParser):
        pass


class SnapFn(PostprocessingFunction):
    @abstractmethod
    def post(self, args: argparse.Namespace, sim: Simulation, snap: Snapshot) -> Result:
        pass

    @abstractmethod
    def plot(self, axes: plt.axes, result: Result):
        pass


class SetFn(PostprocessingFunction):
    @abstractmethod
    def post(self, args: argparse.Namespace, sims: SimulationSet) -> Result:
        pass

    @abstractmethod
    def plot(self, axes: plt.axes, result: Result) -> None:
        pass


class MultiSetFn(PostprocessingFunction):
    @abstractmethod
    def post(self, args: argparse.Namespace, sims: List[SimulationSet]) -> Result:
        pass

    @abstractmethod
    def plot(self, axes: plt.axes, result: Result) -> None:
        pass


class SliceFn(PostprocessingFunction):
    def __init__(self, slice_type: str):
        self.slice_type = slice_type

    @abstractmethod
    def post(self, args: argparse.Namespace, sim: Simulation, slice_: Any) -> Result:
        pass

    @abstractmethod
    def plot(self, axes: plt.axes, result: Result) -> None:
        pass


# Giving up on mypy hints on this one
def addToList(name: Optional[str], fn: PostprocessingFunction) -> Any:
    if name is not None:
        fn.name = name
    else:
        fn.name = fn.__name__
        fn.name = fn.name[0].lower() + fn.name[1:]
    postprocessingFunctions.append(fn)


def checkNoDoubledNames() -> None:
    functionNames: List[str] = [f.name for f in postprocessingFunctions]
    assert len(set(functionNames)) == len(functionNames), "Two functions with the same name in postprocessing functions!"


postprocessingFunctions: List[PostprocessingFunction] = []
