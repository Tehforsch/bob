import numpy as np

# Density: 1 / cm^-3
shadowingDensity = 1.672622012311334e-24
shadowing1Params = {
    "center": np.array([0.5, 0.5, 0.7]),
    "factor": 1000,
    "size": 0.15,
    "baseDensity": shadowingDensity,
}
shadowing2Params = {
    "center": np.array([0.5, 0.5, 0.7]),
    "factor": 1000,
    "size": 0.05,
    "baseDensity": shadowingDensity,
}
shadowingCenterParams = {
    "center": np.array([0.5, 0.5, 0.5]),
    "factor": 1000,
    "size": 0.125,
    "baseDensity": shadowingDensity,
}


def rType(coord: np.ndarray) -> float:
    return 1.672622012311334e-27  # 1e-3 / cm^-3


def dType(coord: np.ndarray) -> float:
    return 1.672622012311334e-27  # 1e-3 / cm^-3


def shadowing(
    coord: np.ndarray,
    center: np.ndarray,
    factor: float,
    size: float,
    baseDensity: float,
) -> float:
    localFactor = factor if np.linalg.norm(coord - center) < size else 1
    return baseDensity * localFactor


def shadowing1(coord: np.ndarray) -> float:
    return shadowing(coord, **shadowing1Params)


def shadowing2(coord: np.ndarray) -> float:
    return shadowing(coord, **shadowing2Params)


def shadowingCenter(coord: np.ndarray) -> float:
    return shadowing(coord, **shadowingCenterParams)
