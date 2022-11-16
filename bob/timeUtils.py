import numpy as np
import astropy.units as pq
from astropy.cosmology import z_at_value, Cosmology
from bob.simType import SimType
from enum import Enum
from typing import TYPE_CHECKING, Callable, Any

if TYPE_CHECKING:
    from bob.simulation import Simulation


class TimeType(Enum):
    TIME = 0
    REDSHIFT = 1
    SCALE_FACTOR = 2
    AGE = 3


def scaleFactorToRedshift(scaleFactor: pq.Quantity) -> pq.Quantity:
    return 1.0 / scaleFactor - 1.0 * pq.dimensionless_unscaled


def lin_interpolated(f: Callable[..., Any]) -> Callable[..., Any]:
    def wrapper(values: pq.Quantity) -> pq.Quantity:
        if values.size > 5000:
            print("Using cached version of redshift -> age conversion for performance reasons")
            nValues = 500
            minValue = np.min(values)
            maxValue = np.max(values)
            xs = np.linspace(minValue, maxValue, nValues)
            ys = f(xs)
            assert np.all(np.diff(xs) > 0)
            return np.interp(values, xs, ys)
        else:
            return f(values)

    return wrapper


def redshiftToAge(cosmology: Cosmology, redshift: pq.Quantity) -> pq.Quantity:
    return lin_interpolated(lambda z: cosmology.age(z))(redshift)


def ageToRedshift(cosmology: Cosmology, age: pq.Quantity) -> pq.Quantity:
    return lin_interpolated(lambda a: z_at_value(cosmology.age, a))(age)


def shiftByIcsTime(sim: "Simulation", values: pq.Quantity) -> pq.Quantity:
    icsTime = sim.icsFile().attrs["Time"]
    cosmology = sim.getCosmology()
    ageIcs = redshiftToAge(cosmology, scaleFactorToRedshift(icsTime))
    ageNow = ageIcs + values
    if ageNow.shape == ():
        redshiftNow = ageToRedshift(cosmology, ageNow)
    else:
        validTimes = np.where(ageNow < np.Infinity)
        redshiftNow = np.ones(ageNow.shape) * np.Infinity
        if validTimes[0].shape[0] > 0:
            redshiftNow[validTimes] = ageToRedshift(cosmology, ageNow[validTimes])
    return cosmology.scale_factor(redshiftNow) * pq.dimensionless_unscaled


class TimeQuantity:
    def __init__(self, sim: "Simulation", values: pq.Quantity) -> None:
        self.sim = sim
        match sim.simType():
            case SimType.HYDRO_COSMOLOGICAL:
                self.type_ = TimeType.SCALE_FACTOR
                self.values = values * pq.dimensionless_unscaled
            case SimType.HYDRO_STANDARD:
                self.type_ = TimeType.TIME
                self.values = values
            case SimType.POST_COSMOLOGICAL:
                self.type_ = TimeType.SCALE_FACTOR
                raise NotImplementedError
            case SimType.POST_STANDARD_ICS_COSMOLOGICAL:
                self.type_ = TimeType.SCALE_FACTOR
                self.values = shiftByIcsTime(sim, values)
            case SimType.POST_STANDARD:
                self.type_ = TimeType.TIME
                self.values = values

    def age(self) -> pq.Quantity:
        if self.type_ == TimeType.SCALE_FACTOR:
            cosmology = self.sim.getCosmology()
            return cosmology.age(self.redshift())
        raise NotImplementedError("")

    def time(self) -> pq.Quantity:
        if self.type_ == TimeType.TIME:
            return self.values
        raise NotImplementedError('Time quantity TIME not implemented for this simulation type. (Try "time: z" ?)')

    def scaleFactor(self) -> pq.Quantity:
        if self.type_ == TimeType.SCALE_FACTOR:
            return self.values
        raise NotImplementedError("")

    def redshift(self) -> pq.Quantity:
        if self.type_ == TimeType.SCALE_FACTOR:
            return scaleFactorToRedshift(self.values)
        raise NotImplementedError("")
