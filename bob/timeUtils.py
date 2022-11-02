import numpy as np
import astropy.units as pq
from astropy.cosmology import z_at_value
from bob.simulation import Simulation, SimType
from enum import Enum


class TimeType(Enum):
    TIME = 0
    REDSHIFT = 1
    SCALE_FACTOR = 2
    AGE = 3


def scaleFactorToRedshift(scaleFactor: pq.Quantity) -> pq.Quantity:
    return 1.0 / scaleFactor - 1.0 * pq.dimensionless_unscaled


def shiftByIcsTime(sim: Simulation, values: pq.Quantity) -> pq.Quantity:
    icsTime = sim.icsFile().attrs["Time"]
    cosmology = sim.getCosmology()
    ageIcs = cosmology.age(z_at_value(cosmology.scale_factor, icsTime))
    ageNow = ageIcs + values
    validTimes = np.where(ageNow < np.Infinity)
    redshiftNow = np.ones(ageNow.shape) * np.Infinity
    if validTimes[0].shape[0] > 0:
        redshiftNow[validTimes] = z_at_value(cosmology.age, ageNow[validTimes])
    return cosmology.scale_factor(redshiftNow) * pq.dimensionless_unscaled


class TimeQuantity:
    def __init__(self, sim: Simulation, values: pq.Quantity) -> None:
        self.sim = sim
        match sim.simType():
            case SimType.HYDRO_COSMOLOGICAL:
                self.type_ = TimeType.SCALE_FACTOR
                self.values = values
            case SimType.HYDRO_STANDARD:
                self.type_ = TimeType.TIME
                self.values = values
            case SimType.POST_COSMOLOGICAL:
                self.type_ = TimeType.SCALE_FACTOR
                self.values = shiftByIcsTime(sim, values)
            case SimType.POST_STANDARD_ICS_COSMOLOGICAL:
                self.type_ = TimeType.SCALE_FACTOR
                self.values = shiftByIcsTime(sim, values)
            case SimType.POST_STANDARD:
                self.type_ = TimeType.TIME
                self.values = values

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

    def scaleFactor(self) -> pq.Quantity:
        assert self.sim.simType().is_cosmological()
        if self.type_ == TimeType.SCALE_FACTOR:
            return self.values
        raise NotImplementedError("")

    def redshift(self) -> pq.Quantity:
        if self.type_ == TimeType.SCALE_FACTOR:
            return scaleFactorToRedshift(self.values)
        raise NotImplementedError("")
