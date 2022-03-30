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

    @property
    @abstractmethod
    def symbol(self) -> str:
        pass

    @property
    @abstractmethod
    def unit(self) -> str:
        pass
