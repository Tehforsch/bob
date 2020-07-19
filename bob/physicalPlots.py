from typing import Callable
import matplotlib.pyplot as plt
import quantities as pq
import numpy as np
from bob.simulationSet import SimulationSet
from bob.snapshot import Snapshot
from bob.slicePlot import Slice
from bob.basicField import BasicField
from bob.postprocessingFunctions import addPlot, addSingleSnapshotPlot
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


def getIonizationRadius(snapshot: Snapshot, center: np.ndarray, val: float = 0.5) -> float:
    coordinates = snapshot.coordinates
    field = BasicField("ChemicalAbundances", 1)
    data = field.getData(snapshot)
    valueFunction = lambda radius: getIonization(coordinates, data, center, radius)
    return bisect(valueFunction, val, 0, 1, precision=0.00001) * snapshot.l_unit


def analyticalRTypeExpansion(t: np.ndarray) -> np.ndarray:
    return (1 - np.exp(-t)) ** (1.0 / 3)


@addPlot(None)
def expansionInnerOuter(ax: plt.axes, sims: SimulationSet) -> None:
    expansionGeneral(ax, sims, innerOuter=True)


@addPlot(None)
def expansion(ax: plt.axes, sims: SimulationSet) -> None:
    expansionGeneral(ax, sims, innerOuter=False)


def expansionGeneral(ax: plt.axes, sims: SimulationSet, innerOuter: bool = False) -> None:
    gridspec_kw = {"height_ratios": [2, 1]}
    _, (ax1, ax2) = ax.subplots(2, sharex=True, sharey=False, gridspec_kw=gridspec_kw)
    ax1.set_xlim(0, 1.0)
    ax1.set_ylim(0, 1.0)
    ax2.set_ylim(0, 0.2)
    ax2.set_xlabel("$t / t_{\\mathrm{rec}}$")
    ax1.set_ylabel("$R / R_s$")
    ax2.set_ylabel("relative error")

    colors = ["b", "orange"]
    for (color, sim) in zip(colors, sims):
        initialSnap = sim.snapshots[0]
        nH = np.mean(BasicField("Density").getData(initialSnap) * initialSnap.dens_prev * initialSnap.dens_to_ndens) * 1.22
        recombinationTime = 1 / (alphaB * nH)
        recombinationTime.units = "Myr"
        nE = nH  # We can probably assume this
        assert len(sim.sources) == 1
        photonRate = sim.sources.sed[0, 2] / pq.s
        stroemgrenRadius = (3 * photonRate / (4 * np.pi * alphaB * nE ** 2)) ** (1 / 3.0)
        stroemgrenRadius.units = "kpc"
        print("Recombination time: {}, Stroemgren radius: {}".format(recombinationTime, stroemgrenRadius))
        times = [(snapshot.time / recombinationTime).simplified for snapshot in sim.snapshots]
        radii = [(getIonizationRadius(snapshot, np.array([0.5, 0.5, 0.5]), 0.5) / stroemgrenRadius).simplified for snapshot in sim.snapshots]
        error = [
            np.abs(radius - analyticalRTypeExpansion(time)) / (1e-10 + analyticalRTypeExpansion(time)) if time > 0 else 0
            for (time, radius) in zip(times, radii)
        ]
        if not innerOuter:
            ax1.plot(times, radii, label=sims.getNiceSimName(sim), color=color)
        else:
            radiiUpper = [(getIonizationRadius(snapshot, np.array([0.5, 0.5, 0.5]), 0.9) / stroemgrenRadius).simplified for snapshot in sim.snapshots]
            radiiLower = [(getIonizationRadius(snapshot, np.array([0.5, 0.5, 0.5]), 0.1) / stroemgrenRadius).simplified for snapshot in sim.snapshots]
            ax1.plot(times, radii, label=sims.getNiceSimName(sim) + " 0.5", color=color)
            ax1.plot(times, radiiUpper, label=sims.getNiceSimName(sim) + " 0.9", color=color, linestyle="--")
            ax1.plot(times, radiiLower, label=sims.getNiceSimName(sim) + " 0.1", color=color, linestyle="--")
        ax2.plot(times, error, label="Relative error")

    ts = np.linspace(0, 1, num=1000)
    ax1.plot(ts, [analyticalRTypeExpansion(t) for t in ts], label="Analytical", color="g")
    ax1.legend()


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
