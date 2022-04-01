import argparse

import matplotlib.pyplot as plt

from abc import ABC, abstractmethod
from typing import Any, List
from bob.simulation import Simulation
from bob.simulationSet import SimulationSet
from bob.snapshot import Snapshot
from bob.result import Result
from bob.multiSet import MultiSet


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
    def setArgs(self, subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument("--slice_field", choices=["xHP", "temp"], required=True)

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
