from typing import Callable, List
import numpy as np
from bob.snapshot import Snapshot
from bob.simulation import Simulation
from bob.util import unitNpArray, fileMemoize
from bob.field import Field


@fileMemoize
def getMeanValue(snap: Snapshot, field: Field) -> float:
    return np.mean(field.getData(snap))


@fileMemoize
def getTimes(sim: Simulation) -> List[float]:
    return unitNpArray([snapshot.time for snapshot in sim.snapshots])


def bisect(valueFunction: Callable[[float], float], targetValue: float, start: float, end: float, precision: float = 0.01) -> float:
    """Find the x at which the monotonously growing function valueFunction fulfills valueFunction(x) = targetValue to a precision (in x) of precision. start and end denote the maximum and minimum possible x value"""
    position = (end + start) / 2
    if (end - start) < precision:
        return position
    value = valueFunction(position)
    if value < targetValue:
        return bisect(valueFunction, targetValue, position, end, precision=precision)
    else:
        return bisect(valueFunction, targetValue, start, position, precision=precision)
