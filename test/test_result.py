from typing import Any
import tempfile
import unittest
from pathlib import Path

import numpy as np
import astropy.units as pq

from bob.result import Result


class Tests(unittest.TestCase):
    @staticmethod
    def getTestResultA() -> Any:
        class A(Result):
            def __init__(self) -> None:
                self.temperature = np.array([1.0, 2.0, 3.0]) * pq.K
                self.lengths = np.array([1.0, 0.0, 0.0]) * pq.m

        return A()

    @staticmethod
    def getTestResultB() -> Any:
        class B(Result):
            def __init__(self) -> None:
                self.densities = [
                    np.array([1.0, 0.0]) * pq.kg / pq.m**3,
                    np.array([2.0, 5.0, 1.0]) * pq.g / pq.m**3,
                    np.array([3.0, 2.0]) * pq.kg / pq.m**3,
                ]
                self.volumes = np.array([0.0, 0.0]) * pq.cm**3
                self.some_other = np.array([5.0, 1.0]) * pq.J

        return B()

    @staticmethod
    def getTestResultC() -> Any:
        class C(Result):
            def __init__(self) -> None:
                self.results = [Tests.getTestResultA(), Tests.getTestResultB()]

        return C()

    def check_write_and_read_result(self, result: Result) -> None:
        with tempfile.TemporaryDirectory() as f:
            folder = Path(f)
            result.save(folder)
            resultRead = Result.readFromFolder(folder)
            self.assert_equal_results(result, resultRead)

    def test_a(self) -> None:
        self.check_write_and_read_result(self.getTestResultA())

    def test_b(self) -> None:
        self.check_write_and_read_result(self.getTestResultB())

    def test_c(self) -> None:
        self.check_write_and_read_result(self.getTestResultC())

    def assert_equal_quantities(self, q1: pq.Quantity, q2: pq.Quantity) -> None:
        assert q1.unit == q2.unit
        assert np.equal(q1.value, q2.value).all()

    def assert_result_contains_other_result(self, res1: Result, res2: Result) -> None:
        for (k, v) in res1.__dict__.items():
            assert k in res2.__dict__
            if type(v) == pq.Quantity:
                self.assert_equal_quantities(res2.__getattribute__(k), v)
            else:
                assert type(v) == list
                if isinstance(v[0], Result):
                    for (subres1, subres2) in zip(v, res2.__getattribute__(k)):
                        self.assert_equal_results(subres1, subres2)
                else:
                    for (q1, q2) in zip(res2.__getattribute__(k), v):
                        self.assert_equal_quantities(q1, q2)

    def assert_equal_results(self, res1: Result, res2: Result) -> None:
        self.assert_result_contains_other_result(res1, res2)
        self.assert_result_contains_other_result(res2, res1)


if __name__ == "__main__":
    unittest.main()
