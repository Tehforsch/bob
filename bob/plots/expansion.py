from typing import List, Tuple
import numpy as np
import matplotlib.pyplot as plt
import quantities as pq
from bob.basicField import BasicField

from bob.simulationSet import SimulationSet
from bob.simulation import Simulation
from bob.postprocessingFunctions import addPlot
from bob.constants import alphaB, protonMass, kB, gamma
from bob.util import unitNpArray, fileMemoize
from bob.snapshot import Snapshot
from bob.helpers import getMeanValue, getTimes, bisect
from bob.temperature import Temperature


def getIonization(coordinates: np.ndarray, data: np.ndarray, center: np.ndarray, radius: float) -> float:
    shellWidth = 0.05
    distanceToCenter = getDistanceToCenter(coordinates, center)
    insideShell = np.where((distanceToCenter > radius - shellWidth / 2) & (distanceToCenter < radius + shellWidth / 2))
    return np.mean(1 - data[insideShell])


def getDistanceToCenter(coordinates: np.ndarray, center: np.ndarray) -> np.ndarray:
    return np.linalg.norm(coordinates - center, axis=1)


def getIonizationRadius(snapshot: Snapshot, center: np.ndarray, val: float = 0.5) -> float:
    coordinates = snapshot.coordinates
    field = BasicField("ChemicalAbundances", 1)
    data = field.getData(snapshot)
    valueFunction = lambda radius: getIonization(coordinates, data, center, radius)
    return bisect(valueFunction, val, 0, 1, precision=0.00001) * snapshot.lengthUnit


def analyticalRTypeExpansion(t: np.ndarray) -> np.ndarray:
    return (1 - np.exp(-t)) ** (1.0 / 3)


def analyticalDTypeExpansion(t: np.ndarray, ci: float, stroemgrenRadius: float) -> np.ndarray:
    return stroemgrenRadius * ((1 + 7 / 4 * ci * t / stroemgrenRadius) ** (4.0 / 7.0)).simplified


@fileMemoize
def getRadii(sim: Simulation, treshold: float = 0.5, sourcePos: np.ndarray = np.array([0.5, 0.5, 0.5])) -> List[float]:
    return unitNpArray([(getIonizationRadius(snapshot, sourcePos, treshold)) for snapshot in sim.snapshots])


@addPlot(None)
def expansionInnerOuter(ax: plt.axes, sims: SimulationSet) -> None:
    expansionGeneral(ax, sims, innerOuter=True)


@addPlot(None)
def expansion(ax: plt.axes, sims: SimulationSet) -> None:
    expansionGeneral(ax, sims, innerOuter=False)


@addPlot(None)
def expansionErrorOverResolution(ax: plt.axes, sims: SimulationSet) -> None:
    quotient = sims.quotient(["ReferenceGasPartMass", "InitCondFile"])
    quotient.sort(key=lambda sims: (sims[0]["SX_SWEEP"]))
    for (params, simSet) in quotient:
        resolutions = [sim.resolution for sim in simSet]
        averageError = [np.mean(getExpansionData(sim)[2]) for sim in simSet]
        plt.xlabel("Resolution")
        plt.ylabel("Error")
        plt.plot(resolutions, averageError, label=sims.getNiceSubsetName(params, simSet), marker="o")
        plt.legend()


def getExpansionData(sim: Simulation) -> Tuple[np.ndarray, np.ndarray, np.ndarray, float, float]:
    initialSnap = sim.snapshots[0]
    meanDens = getMeanValue(initialSnap, BasicField("Density"))
    nH = meanDens * initialSnap.dens_prev * initialSnap.dens_to_ndens * 1.22
    recombinationTime = 1 / (alphaB * nH)
    recombinationTime.units = "Myr"
    nE = nH  # We can probably assume this
    assert len(sim.sources) == 1
    photonRate = sim.sources.sed[0, 2] / pq.s
    stroemgrenRadius = (3 * photonRate / (4 * np.pi * alphaB * nE ** 2)) ** (1 / 3.0)
    stroemgrenRadius.units = "kpc"
    print(f"Mass density: {nH*protonMass}, Number density: {nH}")
    print(f"Recombination time: {recombinationTime}, Stroemgren radius: {stroemgrenRadius}")
    times = (getTimes(sim) / recombinationTime).simplified
    radii = (getRadii(sim) / stroemgrenRadius).simplified
    error = [
        np.abs(radius - analyticalRTypeExpansion(time)) / (1e-10 + analyticalRTypeExpansion(time)) if time > 0 else 0 for (time, radius) in zip(times, radii)
    ]
    return times, radii, error, recombinationTime, stroemgrenRadius


def expansionGeneral(ax: plt.axes, sims: SimulationSet, innerOuter: bool = False) -> None:
    # gridspec_kw = {"height_ratios": [2, 1]}
    # _, (ax1, ax2) = ax.subplots(2, sharex=True, sharey=False, gridspec_kw=gridspec_kw)
    _, (ax1) = ax.subplots(1, sharex=True, sharey=False)
    # ax1.set_xlim(0, 1.0)
    # ax1.set_ylim(0, 1.0)
    # ax2.set_ylim(0, 0.2)
    # ax2.set_xlabel("$t / t_{\\mathrm{rec}}$")
    ax1.set_ylabel("$R / R_s$")
    # ax2.set_ylabel("relative error")

    for sim in sims:
        color, linestyle = getStyle(sim)
        times, radii, error, recombinationTime, stroemgrenRadius = getExpansionData(sim)
        temperatures = [(getAverageTemperature(snap, radius)) for (radius, snap) in zip(radii, sim.snapshots)]
        soundSpeed = [getSoundSpeed(temperature) for temperature in temperatures]
        print("Temperature: {}, Sound speed: {}", temperatures[0], soundSpeed[0])
        if not innerOuter:
            (line1,) = ax1.plot(times, radii, label=sims.getNiceSimName(sim), color=color)
            # line1.set_dashes(linestyle)  # 2pt line, 2pt break, 10pt line, 2pt break
        else:
            radiiUpper = [(getIonizationRadius(snapshot, np.array([0.5, 0.5, 0.5]), 0.9) / stroemgrenRadius).simplified for snapshot in sim.snapshots]
            radiiLower = [(getIonizationRadius(snapshot, np.array([0.5, 0.5, 0.5]), 0.1) / stroemgrenRadius).simplified for snapshot in sim.snapshots]

            ax1.plot(times, radii, label=sims.getNiceSimName(sim) + " 0.5", color=color)
            ax1.plot(times, radiiUpper, label=sims.getNiceSimName(sim) + " 0.9", color=color, linestyle="--")
            ax1.plot(times, radiiLower, label=sims.getNiceSimName(sim) + " 0.1", color=color, linestyle="--")
        # (line2,) = ax2.plot(times, error, label="Relative error", color=color)
        # line2.set_dashes(linestyle)

    ts = np.linspace(0, np.max(times), num=1000)
    # ax1.plot(ts, [analyticalRTypeExpansion(t) for t in ts], label="Analytical", color="g")
    ci = soundSpeed[0]
    ax1.plot(ts, [analyticalDTypeExpansion(t * recombinationTime, ci, stroemgrenRadius) / stroemgrenRadius for t in ts], label="Analytical", color="g")
    ax1.legend()


def getSoundSpeed(temperature: float) -> float:
    return np.sqrt(gamma * kB * temperature / (protonMass)).simplified


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
    cmap = cmaps[int(sim.params["SX_SWEEP"])]
    color = cmap(1.0 - resolutionIndex * 0.05)
    linestyle = [4, resolutionIndex]
    return color, [1]
    return color, linestyle
