from pathlib import Path
import astropy.units as pq
import astropy.cosmology.units as cu
import matplotlib.pyplot as plt
import numpy as np
import h5py
from typing import List, Any

from bob.util import getArrayQuantity
from bob.simulationSet import SimulationSet
from bob.result import Result
from bob.postprocessingFunctions import SetFn
from bob.plotConfig import PlotConfig
from bob.util import getFiles, isclose


class GroupFile:
    def __init__(self, path: Path) -> None:
        self.path = path
        name = path.name
        name = name.replace("fof_subhalo_tab_", "")
        name = name.replace(".hdf5", "")
        split = [int(x) for x in name.split(".")]
        self.f = h5py.File(path)
        self.icsSnap = split[0]
        self.filenum = split[1]

    def __repr__(self) -> str:
        return str(self.path.name)


class GroupFiles:
    def __init__(self, sims: SimulationSet, groupFolder: Path) -> None:
        timeEpsilon = 9e-3  # for testing. increase this eventually
        print("STILL USING VERY LARGE EPSILON, DISABLE")
        originalScaleFactors = [sim.icsFile().attrs["Time"] for sim in sims]
        assert len(originalScaleFactors) > 0
        originalScaleFactor = originalScaleFactors[0]
        assert all(isclose(s, originalScaleFactor) for s in originalScaleFactors)
        groupCatalogs = [GroupFile(f) for f in getFiles(groupFolder) if "fof_subhalo_tab" in f.name]
        self.files = [c for c in groupCatalogs if isclose(c.f["Header"].attrs["Time"], originalScaleFactor, epsilon=timeEpsilon)]

    def joinDatasets(self, getDataset: Any, unit: pq.Quantity) -> pq.Quantity:
        result = None
        for f in self.files:
            q = getDataset(f.f)
            if result is None:
                result = q
            else:
                result = np.concatenate((result, q))
        return result * unit

    def haloMasses(self) -> pq.Quantity:
        print("Shouldn't this be part type = 1? see haloCatalog.py")
        massUnit = 1e10 * pq.Msun / cu.littleh
        return self.joinDatasets(lambda f: f["Group"]["GroupMassType"][...][:, 0], massUnit)

    def stellarMasses(self) -> pq.Quantity:
        massUnit = 1e10 * pq.Msun / cu.littleh
        return self.joinDatasets(lambda f: f["Group"]["GroupMassType"][...][:, 4], massUnit)
