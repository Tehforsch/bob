from bob.helpers import getMeanValue
from bob.postprocessingFunctions import addSingleSnapshotPostprocessing
from bob.snapshot import Snapshot
from bob.simulation import Simulation
from bob.basicField import BasicField
from bob.field import Field
import numpy as np
import quantities as pq

from bob.constants import alphaB
from bob.constants import protonMass
from bob.helpers import getMeanValue


@addSingleSnapshotPostprocessing(None)
def overview(sim: Simulation, snap: Snapshot):
    printStats(snap, BasicField("Density"), "Density")
    # nH = meanDens * snap.dens_prev * snap.dens_to_ndens * 1.22
    # recombinationTime = 1 / (alphaB * nH)
    # recombinationTime.units = "Myr"
    # nE = nH  # We can probably assume this
    # # assert len(sim.sources) == 1
    # photonRate = sim.sources.sed[0, 2] / pq.s
    # stroemgrenRadius = (3 * photonRate / (4 * np.pi * alphaB * nE ** 2)) ** (1 / 3.0)
    # stroemgrenRadius.units = "kpc"
    # print(f"Mass density: {nH*protonMass}")
    # print(f"Number density: {nH}")

def printStats(snap: Snapshot, field: Field, name: str) -> None:
    data = field.getData(snap)
    maxV = np.max(data)
    meanV = np.mean(data)
    minV = np.min(data)
    print(f"{name}:\n\tMax: {maxV}\n\tMean: {meanV}\n\tMin: {minV}\n")


