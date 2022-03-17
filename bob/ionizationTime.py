import matplotlib.pyplot as plt
import numpy as np
from bob.snapshot import Snapshot
from bob.postprocessingFunctions import addSingleSimPlot
from bob.simulationSet import SimulationSet
from bob.simulation import Simulation
from bob.basicField import BasicField
from bob.slicePlot import findOrthogonalAxes
import bob.config as config
from scipy.spatial import cKDTree


@addSingleSimPlot(None)
def ionizationTime(plt: plt.axes, sim: Simulation) -> None:
    axis = np.array([0.0, 0.0, 1.0])
    n1 = config.dpi * 3
    n2 = config.dpi * 3
    data = np.zeros((n1, n2))
    snapshots = sim.snapshots
    snapshots.sort(key=lambda snap: -snap.time)
    for snap in snapshots:
        xHP = BasicField("ChemicalAbundances", 1).getData(snap)
        center = snap.center
        ortho1, ortho2 = findOrthogonalAxes(axis)
        min1 = np.dot(ortho1, snap.minExtent)
        min2 = np.dot(ortho2, snap.minExtent)
        max1 = np.dot(ortho1, snap.maxExtent)
        max2 = np.dot(ortho2, snap.maxExtent)
        p1, p2 = np.meshgrid(np.linspace(min1, max1, n1), np.linspace(min2, max2, n2))
        coordinates = axis * (center * axis) + np.outer(p1, ortho1) + np.outer(p2, ortho2)
        tree = cKDTree(snap.coordinates)
        cellIndices = tree.query(coordinates)[1]
        cellIndices = cellIndices.reshape((n1, n2))
        abundance = xHP[cellIndices]
        data[np.where(abundance > 0.5)] = sim.getRedshift(snap.time)
    plt.xlabel("x")
    plt.ylabel("y")
    extent = (min1, max1, min2, max2)
    plt.imshow(data, extent=extent, origin="lower", cmap="Reds")
    plt.colorbar()
