import unittest

import astropy.units as pq
import numpy as np

from bob.util import getArrayQuantity


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
