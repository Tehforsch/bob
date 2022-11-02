from enum import Enum


class SimType(Enum):
    HYDRO_STANDARD = 0
    HYDRO_COSMOLOGICAL = 1
    POST_STANDARD = 2
    POST_COSMOLOGICAL = 3
    POST_STANDARD_ICS_COSMOLOGICAL = 4
    POST_CASCADE = 5

    def is_cosmological(self) -> bool:
        return self == SimType.HYDRO_COSMOLOGICAL or self == SimType.POST_COSMOLOGICAL

    def can_get_redshift(self) -> bool:
        return self == SimType.HYDRO_COSMOLOGICAL or self == SimType.POST_COSMOLOGICAL or self == SimType.POST_STANDARD_ICS_COSMOLOGICAL
