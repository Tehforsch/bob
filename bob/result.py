from typing import List, Dict, Any
import numpy as np


class Result:
    def __init__(self, arrs: List[np.ndarray], params: Dict[str, Any] = None) -> None:
        self.arrs = arrs
        if params is None:
            self.params = {}
        else:
            self.params = params
