import astropy.units as pq

from typing import Sequence, Optional
import numpy as np
from bob.field import Field
from bob.snapshot import Snapshot


class CombinedField(Field):
    def __init__(self, fields: Sequence[Field], colors: Optional[Sequence[np.ndarray]] = None) -> None:
        if colors is None:
            colors = [
                np.array([1.0, 0.0, 0.0]),
                np.array([0.0, 1.0, 0.0]),
                np.array([0.0, 0.0, 1.0]),
            ]
        self.colors = colors
        self.fields = fields

    def getData(self, snapshot: Snapshot) -> np.ndarray:
        data = [field.getData(snapshot) for field in self.fields]
        return sum((np.outer((d - np.min(d)) / (np.max(d) - np.min(d)), color) for (d, color) in zip(data, self.colors)), np.array([0.0, 0.0, 0.0]))

    @property
    def niceName(self) -> str:
        return "".join(f"{field.niceName}" for field in self.fields)

    @property
    def unit(self) -> pq.Quantity:
        return pq.dimensionless_unscaled

    @property
    def symbol(self) -> str:
        return " ".join(f.symbol for f in self.fields)
