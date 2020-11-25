import numpy as np

shadowing1Params = {"center": np.array([0.5, 0.5, 0.7]), "factor": 1000, "size": 0.15, "baseDensity": 1.672622012311334e-27}
shadowing2Params = {"center": np.array([0.5, 0.5, 0.7]), "factor": 1000, "size": 0.05, "baseDensity": 1.672622012311334e-27}
shadowingCenterParams = {"center": np.array([0.5, 0.5, 0.5]), "factor": 1000, "size": 0.125, "baseDensity": 1.672622012311334e-27}


def homogeneous(coord: np.ndarray) -> float:
    # dist = np.linalg.norm(coord - np.array([0.5, 0.5, 0.5]))
    # return 5.21e-21 / (dist ** 4 + 0.01)  # g/cm^-3
    return 1.672622012311334e-27


def shadowing(coord: np.ndarray, center: np.ndarray, factor: float, size: float, baseDensity: float) -> float:
    localFactor = factor if np.linalg.norm(coord - center) < size else 1
    return baseDensity * localFactor


def shadowing1(coord: np.ndarray) -> float:
    return shadowing(coord, **shadowing1Params)


def shadowing2(coord: np.ndarray) -> float:
    return shadowing(coord, **shadowing2Params)


def shadowingCenter(coord: np.ndarray) -> float:
    return shadowing(coord, **shadowingCenterParams)
