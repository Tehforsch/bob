import numpy as np
import matplotlib.pyplot as plt
from bob.snapshot import Snapshot
from bob.combinedField import CombinedField
from bob.tresholdField import TresholdField
from bob.basicField import BasicField
from bob.slicePlot import voronoiSlice
from bob.postprocessingFunctions import addSingleSnapshotPlot

from bob.config import npRed, npBlue


@addSingleSnapshotPlot(None)
def shadowing(ax: plt.axes, snap: Snapshot) -> None:
    center = np.array([0.5, 0.5, 0.5])
    axis = np.array([1.0, 0.0, 0.0])
    abundance = BasicField("ChemicalAbundances", 1)
    density = BasicField("Density", None)
    criticalDensity = 1e9
    obstacle = TresholdField(density, criticalDensity, 0, 1)
    field = CombinedField([abundance, obstacle], [npRed, npBlue])

    voronoiSlice(ax, snap, field, center, axis)
