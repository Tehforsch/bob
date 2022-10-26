import astropy.units as pq
from bob.simulation import Simulation
from enum import Enum


class TimeType(Enum):
    TIME = 0
    REDSHIFT = 1
    SCALE_FACTOR = 2
    AGE = 3


class TimeQuantity:
    def __init__(self, sim: Simulation, values: pq.Quantity) -> None:
        self.sim = sim
        self.values = values
        if self.sim.simType().is_cosmological():
            self.type_ = TimeType.SCALE_FACTOR
        else:
            self.type_ = TimeType.TIME

    def age(self) -> pq.Quantity:
        assert self.sim.simType().is_cosmological()
        if self.type_ == TimeType.SCALE_FACTOR:
            cosmology = self.sim.getCosmology()
            return cosmology.age(self.redshift())
        raise NotImplementedError("")

    def time(self) -> pq.Quantity:
        assert not self.sim.simType().is_cosmological()
        if self.type_ == TimeType.TIME:
            return self.values
        raise NotImplementedError("")

    def redshift(self) -> pq.Quantity:
        assert self.sim.simType().is_cosmological()
        if self.type_ == TimeType.SCALE_FACTOR:
            return 1.0 / self.values - 1.0 * pq.dimensionless_unscaled
