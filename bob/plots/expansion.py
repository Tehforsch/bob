from typing import List, Tuple, Callable
import numpy as np
import matplotlib.pyplot as plt
import astropy.units as u

from bob.basicField import BasicField
from bob.simulation import Simulation
from bob.snapshot import Snapshot
from bob.temperature import Temperature
from bob.plots.timePlots import TimePlot
from bob.plotConfig import PlotConfig
from bob.util import getArrayQuantity
from bob.result import Result


def getIonization(coordinates: np.ndarray, data: np.ndarray, boxSize: u.Quantity, center: np.ndarray, radius: float) -> float:
    shellWidth = boxSize * 0.01
    distanceToCenter = getDistanceToCenter(coordinates, center)
    insideShell = np.where((distanceToCenter > radius - shellWidth / 2) & (distanceToCenter < radius + shellWidth / 2))
    return np.mean(1 - data[insideShell])


def getDistanceToCenter(coordinates: np.ndarray, center: np.ndarray) -> np.ndarray:
    return np.linalg.norm(coordinates - center, axis=1)


def getIonizationRadius(snapshot: Snapshot, center: np.ndarray, boxSize: u.Quantity, val: float = 0.5) -> u.Quantity:
    coordinates = snapshot.coordinates
    field = BasicField("ChemicalAbundances", 1)
    data = field.getData(snapshot)

    def valueFunction(radius: u.Quantity) -> u.Quantity:
        return getIonization(coordinates, data, boxSize, center, radius)

    return bisect(valueFunction, val, boxSize * 0.0, boxSize * 0.5, precision=0.00001)


def analyticalRTypeExpansion(t: np.ndarray) -> np.ndarray:
    return (1 - np.exp(-t)) ** (1.0 / 3)


def bisect(
    valueFunction: Callable[[u.Quantity], u.Quantity],
    targetValue: u.Quantity,
    start: u.Quantity,
    end: u.Quantity,
    precision: float = 0.01,
    depth: int = 0,
) -> u.Quantity:
    """Find the x at which the monotonously growing function valueFunction fulfills valueFunction(x) = targetValue to a precision (in x) of precision. start and end denote the maximum and minimum possible x value"""
    position = (end + start) / 2
    if depth > 100:
        print("Failed to bisect")
        return position
    if (end - start) / (abs(end) + abs(start)) < precision:
        return position
    value = valueFunction(position)
    if value < targetValue:
        return bisect(valueFunction, targetValue, position, end, precision=precision, depth=depth + 1)
    else:
        return bisect(valueFunction, targetValue, start, position, precision=precision, depth=depth + 1)


class Expansion(TimePlot):
    def __init__(self, config: PlotConfig) -> None:
        super().__init__(config)
        self.config.setDefault("yUnit", u.kpc)
        self.config.setDefault("legend_loc", "lower right")

    def ylabel(self) -> str:
        return "r"

    def getQuantity(self, sim: Simulation, snap: Snapshot) -> float:
        center = sim.boxSize() / 2.0
        data = getIonizationRadius(snap, center, sim.boxSize())
        return data

    def plot(self, plt: plt.axes, result: Result) -> None:
        super().plot(plt, result)
        plt.legend(loc=self.config["legend_loc"])
        recombination_time = 122.34 * u.Myr
        stroemgren_radius = 6.79 * u.kpc
        self.addLine(
            result.data[0].times,
            stroemgren_radius * analyticalRTypeExpansion(result.data[0].times / recombination_time),
            label="analytical",
            linestyle="--",
        )


def getSoundSpeed(temperature: float) -> float:
    return np.sqrt(gamma * kB * temperature / (protonMass)).decompose()


def getAverageTemperature(snapshot: Snapshot, radius: float) -> np.ndarray:
    temperature = Temperature().getData(snapshot)
    return np.mean(temperature[np.where(getDistanceToCenter(snapshot.coordinates, snapshot.center))])


def getStyle(sim: Simulation) -> Tuple[Tuple[float, float, float], List[float]]:
    try:
        resolution = int(sim.params["InitCondFile"].replace("ics_", ""))
        resolutionIndex = [256, 128, 64, 32].index(resolution)
    except ValueError:
        resolutionIndex = 0
    cmaps = [plt.get_cmap("Reds"), plt.get_cmap("Blues")]
    cmap = cmaps[int(sim.params["SWEEP"])]
    color = cmap(1.0 - resolutionIndex * 0.05)
    linestyle = [4, resolutionIndex]
    return color, [1]
    return color, linestyle
