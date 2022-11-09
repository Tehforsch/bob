import astropy.units as pq
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bob.snapshot import Snapshot


class Field(ABC):
    @abstractmethod
    def getData(self, snapshot: "Snapshot") -> pq.Quantity:
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
