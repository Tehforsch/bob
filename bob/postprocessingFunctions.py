from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from abc import ABC, abstractmethod
from typing import Callable, Any, List, Optional
from bob.simulation import Simulation
from bob.simulationSet import SimulationSet
from bob.snapshot import Snapshot


class PostprocessingFunction(ABC):
    pass


class SnapFn(PostprocessingFunction):
    @abstractmethod
    def post(self, sim: Simulation, snap: Snapshot) -> List[np.ndarray]:
        pass

    @abstractmethod
    def plot(self, axes: plt.axes, result: List[np.ndarray]):
        pass


class SetFn(PostprocessingFunction):
    @abstractmethod
    def post(self, sims: SimulationSet) -> List[np.ndarray]:
        pass

    @abstractmethod
    def plot(self, axes: plt.axes, result: List[np.ndarray]) -> None:
        pass


class MultiSetFn(PostprocessingFunction):
    @abstractmethod
    def post(self, sims: List[SimulationSet]) -> List[np.ndarray]:
        pass

    @abstractmethod
    def plot(self, axes: plt.axes, result: List[np.ndarray]) -> None:
        pass


class SliceFn(PostprocessingFunction):
    def __init__(self, slice_type: str):
        self.slice_type = slice_type

    @abstractmethod
    def post(self, sim: Simulation, slice_: Any) -> List[np.ndarray]:
        pass

    @abstractmethod
    def plot(self, axes: plt.axes, result: List[np.ndarray]) -> None:
        pass


# Giving up on mypy hints on this one
def addToList(name: Optional[str]) -> Any:
    def wrapper(cls: Any) -> Any:
        if name is not None:
            cls.name = name
        else:
            cls.name = cls.__name__
            cls.name = cls.name[0].lower() + cls.name[1:]
        postprocessingFunctions.append(cls)
        return cls

    return wrapper


def checkNoDoubledNames() -> None:
    functionNames: List[str] = [f.name for f in postprocessingFunctions]
    assert len(set(functionNames)) == len(functionNames), "Two functions with the same name in postprocessing functions!"


postprocessingFunctions: List[PostprocessingFunction] = []


def functionNames() -> List[str]:
    return [f.name for f in postprocessingFunctions]
