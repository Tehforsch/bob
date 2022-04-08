import argparse

import matplotlib.pyplot as plt

from bob.simulation import Simulation
from bob.snapshot import Snapshot
from bob.postprocessingFunctions import SnapFn, addToList
from bob.result import Result
from bob.basicField import BasicField
from bob.temperature import Temperature


class TemperatureDensityHistogram(SnapFn):
    def post(self, args: argparse.Namespace, sim: Simulation, snap: Snapshot) -> Result:
        temperature = Temperature().getData(snap)
        density = BasicField("Density").getData(snap)
        return Result([temperature, density])

    def plot(self, plt: plt.axes, result: Result) -> None:
        plt.xlabel("T")
        plt.ylabel("$\rho$")
        plt.hist2d(result.arrs[0], result.arrs[1], [10, 10])
        plt.colorbar()


addToList("temperatureDensityHistogram", TemperatureDensityHistogram())
