from pathlib import Path
import astropy.units as pq
import astropy.cosmology.units as cu
import numpy as np
import h5py
from typing import Any

from bob.simulationSet import SimulationSet
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
        timeEpsilon = 9e-8
        originalScaleFactors = [sim.icsFile().attrs["Time"] for sim in sims]
        assert len(originalScaleFactors) > 0
        originalScaleFactor = originalScaleFactors[0]
        assert all(isclose(s, originalScaleFactor) for s in originalScaleFactors)
        groupCatalogs = [GroupFile(f) for f in getFiles(groupFolder) if "fof_subhalo_tab" in f.name]
        self.files = [c for c in groupCatalogs if isclose(c.f["Header"].attrs["Time"], originalScaleFactor, epsilon=timeEpsilon)]
        assert len(self.files) > 0, f"no group catalog files found for scale factor: {originalScaleFactor}"

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
        massUnit = 1e10 * pq.Msun / cu.littleh
        return self.joinDatasets(lambda f: f["Subhalo"]["SubhaloMassType"][...][:, 1], massUnit)

    def stellarMasses(self) -> pq.Quantity:
        massUnit = 1e10 * pq.Msun / cu.littleh
        return self.joinDatasets(lambda f: f["Subhalo"]["SubhaloMassType"][...][:, 4], massUnit)

    def center_of_mass(self) -> pq.Quantity:
        return self.joinDatasets(lambda f: f["Subhalo"]["SubhaloCM"][...], pq.kpc / cu.littleh)

    def halfmass_rad(self) -> pq.Quantity:
        return self.joinDatasets(lambda f: f["Subhalo"]["SubhaloHalfmassRad"][...], pq.kpc / cu.littleh)
