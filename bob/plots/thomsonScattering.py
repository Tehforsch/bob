from typing import List
import astropy.units as pq
from bob.simulationSet import SimulationSet
import matplotlib.pyplot as plt
import numpy as np

from bob.postprocessingFunctions import addMultiPlot
from bob.basicField import BasicField
from bob.constants import speedOfLight, protonMass


@addMultiPlot(None)
def thomsonScattering(ax1: plt.axes, simSets: List[SimulationSet]) -> None:
    sig = 6.65e-29 * pq.m ** 2  # Thomson scattering cross-section in m^2

    # ne, free electron density in number per m^3

    # dT, the time resolution, so time between steps in years

    for simSet in simSets:
        snapshots = [(snap, sim) for sim in simSet for snap in sim.snapshots]
        snapshots.sort(key=lambda snapSim: -snapSim[0].time)
        redshifts = np.zeros(len(snapshots) - 1)
        dTau = np.zeros(len(snapshots) - 1)
        for (i, ((prevSnap, _), (snap, sim))) in enumerate(zip(snapshots, snapshots[1:])):
            xe = BasicField("ElectronAbundance").getData(snap)
            density = BasicField("Density").getData(snap) * snap.lengthUnit ** (-3) * snap.massUnit
            ne = xe * density / protonMass
            dT = sim.getLookbackTime(snap.scale_factor) - sim.getLookbackTime(prevSnap.scale_factor)
            redshifts[i] = sim.getRedshift(snap.scale_factor)
            dTau[i] = speedOfLight * sig * np.mean(ne) * dT  # dTau at redshift index iz

        plt.plot(redshifts, np.cumsum(dTau))
        plt.xlabel("z")
        plt.ylabel("$\\tau$")
        plt.xlim(5, 11)

        nx = int(50)
        ztau = np.linspace(0.0, 50.0, nx)
        taumax = np.full(nx, 0.061)
        taumin = np.full(nx, 0.047)

        plt.fill_between(ztau, taumin, taumax, facecolor="gray", alpha=0.25, label=r"Planck+18")
