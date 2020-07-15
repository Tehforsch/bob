import numpy as np
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bob.snapshot import Snapshot


class Field(ABC):
    @abstractmethod
    def getData(self, snapshot: "Snapshot") -> np.ndarray:
        pass

    @property
    @abstractmethod
    def niceName(self) -> str:
        pass


class RelativeDifference(Field):
    def __init__(self, field1: Field, field2: Field) -> None:
        self.field1 = field1
        self.field2 = field2

    def getData(self, snapshot: "Snapshot") -> np.ndarray:
        epsilon = 1e-10
        data1 = self.field1.getData(snapshot)
        data2 = self.field2.getData(snapshot)
        return (data1 - data2) / (0.5 * (np.abs(data1) + np.abs(data2)) + epsilon)

    def getNiceName(self) -> str:
        f1 = self.field1.niceName
        f2 = self.field2.niceName
        return f"Rel. Difference ({f1} - {f2})"
