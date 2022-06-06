from typing import List
import itertools

import unittest
from pathlib import Path
import numpy as np
import astropy.units as pq


def getCommonParentFolder(folders: List[Path]) -> Path:
    parts = (folder.parts for folder in folders)
    zippedParts = zip(*parts)
    commonParts = (parts[0] for parts in itertools.takewhile(lambda parts: all(part == parts[0] for part in parts), zippedParts))
    return Path(*commonParts)


def getArrayQuantity(quantities: List[pq.Quantity]) -> pq.Quantity:
    unit = 1.0 * quantities[0].unit
    for y in quantities:
        if not (y / unit).decompose().unit == "":
            raise ValueError("Different units in quantity array")
    return np.array([(y / unit).decompose().value for y in quantities]) * unit


class Test(unittest.TestCase):
    def test_get_array_quantity(self) -> None:
        a = [1.0 * pq.m, 1.0 * pq.cm]
        result = getArrayQuantity(a)
        assert (result.value == np.array([1.0, 0.01])).all()
        assert result.unit == pq.m

    def test_array_quantity_fails_if_given_different_units(self) -> None:
        # try:
        a = [1.0 * pq.m, 1.0 * pq.J]
        try:
            getArrayQuantity(a)
            assert False
        except ValueError:
            pass
