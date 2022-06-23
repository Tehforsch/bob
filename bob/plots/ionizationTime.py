import argparse

import matplotlib.pyplot as plt
import numpy as np
import astropy.units as pq

from bob.simulationSet import SimulationSet
from bob.basicField import BasicField
from bob.result import Result
from bob.postprocessingFunctions import SetFn, addToList
from bob.plots.bobSlice import getSlice
from bob.plots.ionization import translateTime


class IonizationTime(SetFn):
    def post(self, args: argparse.Namespace, simSet: SimulationSet) -> Result:
        self.quantity = args.time
        data = self.getIonizationTimeData(simSet)
        result = Result()
        result.data = data
        return result

    def plot(self, plt: plt.axes, result: Result) -> None:
        self.style.setDefault("cLabel", "$t [\\mathrm{Myr}]$")
        self.style.setDefault("xUnit", pq.Mpc)
        self.style.setDefault("yUnit", pq.Mpc)
        self.style.setDefault("xLabel", "$x [h^{-1} \\mathrm{UNIT}]$")
        self.style.setDefault("yLabel", "$y [h^{-1} \\mathrm{UNIT}]$")
        self.style.setDefault("vUnit", pq.Myr)
        self.style.setDefault("vLim", (0.0, 2e2))
        self.setupLabels()

        vmin, vmax = self.style["vLim"]
        self.image(result.data, self.extent, cmap="Reds", vmin=vmin, vmax=vmax)

    def getIonizationTimeData(self, simSet: SimulationSet) -> pq.Quantity:
        ionizationTime = None
        for sim in simSet:
            if len(sim.snapshots) == 0:
                print("No snapshots in sim? Continuing.")
                continue
            snap = sim.snapshots[-1]
            (self.extent, newIonizationTime) = getSlice(BasicField("IonizationTime"), snap, "z")
            redshift, scale_factor = translateTime(sim, newIonizationTime)
            ionizationTime = redshift
            if ionizationTime is None:
                ionizationTime = newIonizationTime
            else:
                unit = ionizationTime.unit
                value1 = ionizationTime.to(unit).value
                value2 = newIonizationTime.to(unit).value
                ionizationTime = np.minimum(value1, value2) * unit
        if ionizationTime is not None:
            return ionizationTime
        else:
            raise ValueError("No sims/snaps")


addToList("ionizationTime", IonizationTime())
