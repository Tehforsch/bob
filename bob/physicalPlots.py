from typing import Callable
import matplotlib.pyplot as plt
import quantities as pq
import numpy as np
from bob.simulationSet import SimulationSet
from bob.snapshot import Snapshot
from bob.slicePlot import Slice
from bob.basicField import BasicField
from bob.postprocessingFunctions import addPlot, addSingleSnapshotPlot
from bob.util import getNiceTimeUnitName
from bob.constants import alphaB

basicFields = [
    BasicField("ChemicalAbundances", 0),
    BasicField("ChemicalAbundances", 1),
    BasicField("ChemicalAbundances", 2),
    BasicField("ChemicalAbundances", 3),
    BasicField("ChemicalAbundances", 4),
    BasicField("ChemicalAbundances", 5),
    BasicField("Density", None),
    BasicField("PhotonFlux", 0),
    BasicField("PhotonFlux", 1),
    BasicField("PhotonFlux", 2),
    BasicField("PhotonFlux", 3),
    BasicField("PhotonFlux", 4),
    BasicField("PhotonRates", 0),
    BasicField("PhotonRates", 1),
    BasicField("PhotonRates", 2),
    BasicField("PhotonRates", 3),
    BasicField("PhotonRates", 4),
]


def bisect(valueFunction: Callable[[float], float], targetValue: float, start: float, end: float, precision: float = 0.01) -> float:
    """Find the x at which the monotonously growing function valueFunction fulfills valueFunction(x) = targetValue to a precision (in x) of precision. start and end denote the maximum and minimum possible x value"""
    position = (end + start) / 2
    if (end - start) < precision:
        return position
    value = valueFunction(position)
    if value < targetValue:
        return bisect(valueFunction, targetValue, position, end, precision=precision)
    else:
        return bisect(valueFunction, targetValue, start, position, precision=precision)


def getIonization(coordinates: np.ndarray, data: np.ndarray, center: np.ndarray, radius: float) -> float:
    shellWidth = 0.05
    insideShell = np.where(
        (np.linalg.norm(coordinates - center, axis=1) > radius - shellWidth / 2) & (np.linalg.norm(coordinates - center, axis=1) < radius + shellWidth / 2)
    )
    return np.mean(1 - data[insideShell])


def getIonizationRadius(snapshot: Snapshot, center: np.ndarray) -> float:
    coordinates = snapshot.coordinates
    field = BasicField("ChemicalAbundances", 1)
    data = field.getData(snapshot)
    valueFunction = lambda radius: getIonization(coordinates, data, center, radius)
    return bisect(valueFunction, 0.5, 0, 1, precision=0.001) * snapshot.l_unit


@addPlot(None)
def expansion(ax: plt.axes, sims: SimulationSet) -> None:
    ax.xlim(0, 1)
    ax.ylim(0, 1)
    for sim in sims:
        niceTimeUnitName = getNiceTimeUnitName(sim.snapshots[0].t_unit)
        ax.xlabel("$t / t_{\\mathrm{rec}}$")
        ax.ylabel("$R / R_s$")
        initialSnap = sim.snapshots[0]
        nH = np.mean(BasicField("Density").getData(initialSnap) * initialSnap.dens_prev * initialSnap.dens_to_ndens)
        recombinationTime = 1 / (alphaB * nH)
        recombinationTime.units = "Myr"
        nE = nH  # We can probably assume this
        assert len(sim.sources) == 1
        photonRate = sim.sources.sed[0, 2] / pq.s
        stroemgrenRadius = (3 * photonRate / (4 * np.pi * alphaB * nE ** 2)) ** (1 / 3.0)
        stroemgrenRadius.units = "kpc"
        print("Recombination time: {}, Stroemgren radius: {}".format(recombinationTime, stroemgrenRadius))
        times = [(snapshot.time / recombinationTime).simplified for snapshot in sim.snapshots]
        radii = [(getIonizationRadius(snapshot, np.array([0.5, 0.5, 0.5])) / stroemgrenRadius).simplified for snapshot in sim.snapshots]
        ax.plot(times, radii, label=sims.getNiceSimName(sim))
        ax.legend()

    def analytical(t: np.ndarray) -> np.ndarray:
        return (1 - np.exp(-t)) ** (1.0 / 3)

    ts = np.linspace(0, 1, num=100)
    # print(ts, [analytical(t) for t in ts])
    ax.plot(ts, [analytical(t) for t in ts])


def createSlicePlots() -> None:
    for basicField in basicFields:
        for (axis, axisName) in zip([[1, 0, 0], [0, 1, 0], [0, 0, 1]], ["X", "Y", "Z"]):
            center = [0.5, 0.5, 0.5]

            def thisSlicePlot(ax: plt.axes, snap: Snapshot, basicField: BasicField = basicField) -> None:
                # center = sim.boxSize * 0.5
                Slice(snap, basicField, center, axis).plot(ax)

            name = f"centerSlice{axisName}{basicField.niceName}"
            # Register plot in list
            addSingleSnapshotPlot(name)(thisSlicePlot)


createSlicePlots()
