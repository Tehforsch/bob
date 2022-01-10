import numpy as np
from bob.field import Field
from bob.snapshot import Snapshot


class TresholdField(Field):
    def __init__(
        self, field: Field, treshold: float, lowerValue: float, upperValue: float
    ) -> None:
        self.field = field
        self.treshold = treshold
        self.lowerValue = lowerValue
        self.upperValue = upperValue

    def getData(self, snapshot: Snapshot) -> np.ndarray:
        data = self.field.getData(snapshot)
        data[np.where(data <= self.treshold)] = self.lowerValue
        data[np.where(data > self.treshold)] = self.upperValue
        return data

    @property
    def niceName(self) -> str:
        return f"{self.field.niceName} > {self.treshold}"
