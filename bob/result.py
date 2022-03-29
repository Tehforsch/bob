from pathlib import Path
from typing import List, Dict, Any
import numpy as np


class Result:
    def __init__(self, arrs: List[np.ndarray]) -> None:
        self.arrs = arrs

    def save(self, folder: Path):
        for (i, arr) in result.arrs:
            np.save(plotDataFolder / str(i), arr)
