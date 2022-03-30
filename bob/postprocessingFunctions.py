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
    name = ""

    def setArgs(self, subparser: argparse.ArgumentParser) -> None:
        pass

    def getName(self, args: argparse.Namespace) -> str:
        return self.name


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


class MultiSetFn(PostprocessingFunction):
    @abstractmethod
    def post(self, args: argparse.Namespace, sims: List[SimulationSet]) -> Result:
        pass

    @abstractmethod
    def plot(self, axes: plt.axes, result: Result) -> None:
        pass


class SliceFn(PostprocessingFunction):
    def setArgs(self, subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument("--slice_field", choices=["xHP"], required=True)

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


def checkNoDoubledNames() -> None:
    functionNames: List[str] = [f.name for f in postprocessingFunctions]
    assert len(set(functionNames)) == len(functionNames), "Two functions with the same name in postprocessing functions!"


postprocessingFunctions: List[PostprocessingFunction] = []
