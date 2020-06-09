import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from math import sqrt
import itertools

from slicePlot import Slice
from scatter3D import Scatter3D, get3DAx
from snapshot import Snapshot

boxSize = 1


def plotSubplots(subplots, plotSubdivisions=None):
    if plotSubdivisions is None:
        xNum = int(sqrt(len(subplots)))
        yNum = ((xNum - 1) + len(subplots)) // xNum
    else:
        xNum, yNum = plotSubdivisions
    fig, axs = plt.subplots(xNum, yNum)
    if type(axs[0]) == np.ndarray:  # Flatten the list
        axs = [item for sublist in axs for item in sublist]
    for (subplot, ax) in zip(subplots, axs):
        subplot.plot(ax, cmap=plt.cm.cool)
    plt.show()


def getAllSnapshots(simFolder):
    snapshotFiles = list(simFolder.glob("snap_*.hdf5"))
    snapshotFiles.sort()
    return [Snapshot(s) for s in snapshotFiles]


def showSlicesForAllSnapshots(simFolder, fields, start, axis):
    snapshots = getAllSnapshots(simFolder)
    for snapshot in snapshots:
        plotSubplots([Slice(snapshot, field, start, axis) for field in fields])


def showSliceOverTime(simFolder, fields, start, axis):
    snapshots = getAllSnapshots(simFolder)
    slices = [Slice(snap, field, start, axis) for (snap, field) in (itertools.product(snapshots, fields))]
    if len(fields) == 1:
        plotSubplots(slices)
    else:
        plotSubplots(slices, (len(snapshots), len(fields)))


def showSliceAlongAxis(snapshot, fields, axis, numSlices=16):
    origin = np.array([0.0, 0.0, 0.0])
    starts = [origin + boxSize * axis * t for t in np.linspace(0, 1, numSlices)]
    slices = [Slice(snapshot, field, start, axis) for (start, field) in (itertools.product(starts, fields))]
    if len(fields) == 1:
        plotSubplots(slices)
    else:
        plotSubplots(slices, (numSlices, len(fields)))


def showRegions3D(snapshots, field, treshold):
    ax = get3DAx()
    for snapshot in snapshots:
        Scatter3D(snapshot, field, treshold).plot(ax, alpha=1 / (len(snapshots)), s=4.5)
    plt.show()


def main():
    start = np.array([0.5, 0.5, 0.5])
    axis = np.array([1.0, 0.0, 0.0])
    folder = Path(sys.argv[1])
    fields = [
        ("ChemicalAbundances", 0),
        ("ChemicalAbundances", 1),
        ("ChemicalAbundances", 2),
        ("ChemicalAbundances", 3),
        ("ChemicalAbundances", 4),
        ("ChemicalAbundances", 5),
        ("Density", None),
        ("PhotonFlux", 0),
        ("PhotonFlux", 1),
        ("PhotonFlux", 2),
        ("PhotonFlux", 3),
        ("PhotonFlux", 4),
        ("PhotonRates", 0),
        ("PhotonRates", 1),
        ("PhotonRates", 2),
        ("PhotonRates", 3),
        ("PhotonRates", 4),
    ]
    # showSlicesForAllSnapshots(folder, fields, start, axis)
    fields = [
        # ("ChemicalAbundances", 0),
        # ("ChemicalAbundances", 1),
        # ("ChemicalAbundances", 2),
        # ("ChemicalAbundances", 3),
        # ("ChemicalAbundances", 4),
        # ("ChemicalAbundances", 5),
        ("Density", None)
    ]
    # showSliceOverTime(folder, fields, start, axis)
    snapshots = getAllSnapshots(folder)
    showSliceAlongAxis(snapshots[5], fields, axis)
    # showRegions3D(snapshots, ("ChemicalAbundances", 1), 0.5)


main()

# PartType0 / Header
# PartType0 -> ['ChemicalAbundances', 'Coordinates', 'Density', 'InternalEnergy', 'Masses', 'ParticleIDs', 'PhotonFlux', 'PhotonRates', 'Velocities', 'task']
