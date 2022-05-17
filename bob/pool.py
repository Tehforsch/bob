from typing import Any, Callable, List
import multiprocessing
from bob.config import numProcesses


def runInPool(fn: Callable[..., Any], items: List[Any], *args: Any) -> Any:
    with multiprocessing.Pool(numProcesses) as pool:
        return pool.starmap(fn, zip(*[[arg for _ in items] for arg in args], items))
