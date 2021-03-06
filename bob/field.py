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
    def __init__(self, field: Field, reference: "Snapshot") -> None:
        self.field = field
        self.reference = reference

    def getData(self, snapshot: "Snapshot") -> np.ndarray:
        epsilon = 1e-10
        data1 = self.field.getData(snapshot)
        data2 = self.field.getData(self.reference)
        # data2 = reorder(data2, snapshot.coordinates, self.reference.coordinates)
        assert (snapshot.coordinates == self.reference.coordinates).all()
        for (x1, x2, y1, y2) in zip(snapshot.coordinates, self.reference.coordinates, data1, data2):
            assert (x1 == x2).all()
            if np.abs(y1 - y2) > 0.01:
                print(x1, x2, y1, y2)
        print(snapshot, self.reference)
        print(np.sum(np.abs(data1 - data2)))
        return (data1 - data2) / (0.5 * (np.abs(data1) + np.abs(data2)) + epsilon)

    @property
    def niceName(self) -> str:
        name = self.field.niceName
        return f"Rel. Difference {name}"


def reorder(values: np.ndarray, l1: np.ndarray, l2: np.ndarray) -> np.ndarray:
    """Shuffle the order of values and l1 in the same way, such that l1 == l2 and then return the shuffled values"""
    indices = [l2.index(x) for x in l1]
    print(indices)
    return values[indices]
