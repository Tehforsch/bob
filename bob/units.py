import quantities as pq
from bob.constants import MSun


def setupUnits() -> None:
    pq.UnitQuantity("Megayear", pq.yr * 1e6, symbol="Myr")
    pq.UnitQuantity("Kiloparsec", pq.pc * 1e3, symbol="kpc")
    pq.UnitQuantity("Megaparsec", pq.pc * 1e6, symbol="Mpc")
    pq.UnitQuantity("Sun mass", MSun, symbol="MSun")
