import logging

from pathlib import Path
from typing import List, Dict, Any
import numpy as np
import astropy.units as pq


class Result:
    def __init__(self, arrs: List[np.ndarray]) -> None:
        self.arrs = arrs

    def save(self, folder: Path):
        for (i, arr) in enumerate(self.arrs):
            if type(arr) == pq.Quantity:
                value = arr.value
                logging.warning(f"Saving array with units: {arr.unit}")
            else:
                value = arr
            np.save(folder / str(i), value)
