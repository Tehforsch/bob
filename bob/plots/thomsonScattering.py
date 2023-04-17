import astropy.units as pq
import astropy.cosmology.units as cu
import matplotlib.pyplot as plt
import numpy as np

from bob.util import getArrayQuantity
from bob.snapshot import Snapshot
from bob.basicField import BasicField
from bob.constants import speedOfLight, protonMass
from bob.plots.timePlots import getAllSnapshotsWithTime
from bob.result import Result
from bob.electronAbundance import ElectronAbundance
from bob.postprocessingFunctions import MultiSetFn
from bob.plotConfig import PlotConfig
from bob.multiSet import MultiSet


def getRateForSnap(snap: Snapshot) -> pq.Quantity:
    sig = 6.65e-29 * pq.m**2  # Thomson scattering cross-section
    xe = ElectronAbundance().getData(snap)
    density = BasicField("Density").getData(snap).to(pq.g / pq.cm**3, cu.with_H0(snap.H0))
    ne = xe * density / protonMass
    return speedOfLight * sig * np.mean(ne)


class ThomsonScattering(MultiSetFn):
    def __init__(self, config: PlotConfig) -> None:
        super().__init__(config)
        config.setDefault("xLabel", "$z$")
        config.setDefault("xUnit", pq.dimensionless_unscaled)
        config.setDefault("yLabel", "$\\tau$")
        config.setDefault("yUnit", pq.dimensionless_unscaled)
        config.setDefault("xLim", [0, 20])
        config.setDefault("yLim", [0, 0.25])

    def post(self, simSet: MultiSet) -> Result:
        result = Result()
        result.redshifts = []
        result.tau = []
        for sims in simSet:
            snapshots = getAllSnapshotsWithTime("z", sims)
            redshifts = [redshift for (_, _, redshift) in snapshots]
            # Why the fuck does lookback time return a time around ~13 Gyr, whereas
            # age returns small numbers? Am I dumb? shouldnt these be reversed?
            ages = [sim.getLookbackTime(snap.scale_factor) for (snap, sim, _) in snapshots]
            # make sure we "integrate" all the way to z = 0, by pretending that the last snapshot is also valid for z = 0
            redshifts.insert(0, pq.dimensionless_unscaled * 0)
            ages.insert(0, sims[0].getLookbackTime(1.0 * pq.dimensionless_unscaled))
            ages = getArrayQuantity(ages)
            dt = np.diff(ages)

            dTau = [dt[i] * getRateForSnap(snapshots[i][0]) for i in range(len(dt))]
            result.redshifts.append(getArrayQuantity(redshifts))
            tau = np.cumsum(dTau) * pq.dimensionless_unscaled
            # again, insert an additional data point for z = 0
            tau = np.concatenate((np.array([0.0]) * pq.dimensionless_unscaled, tau))
            result.tau.append(tau)
        return result

    def plot(self, plt: plt.axes, result: Result) -> None:
        self.setupLinePlot()
        for redshifts, taus, label in zip(result.redshifts, result.tau, self.getLabels()):
            self.addLine(redshifts, taus, label=label)
        plt.legend()
        nx = int(50)
        ztau = np.linspace(0.0, 50.0, nx)
        taumax = np.full(nx, 0.061)
        taumin = np.full(nx, 0.047)

        plt.fill_between(ztau, taumin, taumax, facecolor="gray", alpha=0.25, label=r"Planck+18")
