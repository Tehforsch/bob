import os
from pathlib import Path

import numpy as np
from typing import Dict, Any, List, Tuple, Union
import yaml
from astropy.cosmology import FlatLambdaCDM, z_at_value
import astropy.units as pq
from enum import Enum

import bob.config as config
from bob.snapshot import Snapshot
from bob.sources import Sources


def getParams(folder: Path) -> Dict[str, Any]:
    bobParamsFile = folder / "bobParams.yaml"
    contents = yaml.load(bobParamsFile.open("r"), Loader=yaml.SafeLoader)
    result = {}
    for (k, v) in contents.items():
        if v == "None":
            continue
        readValue = getParamValue(*list(v.items())[0])
        result[k] = readValue
    return result


def getParamValue(type_: str, value: Any) -> Union[str, bool, int, float, List[int], List[bool], List[float], List[str]]:
    if type_ == "Bool":
        return bool(value)
    if type_ == "Str":
        return str(value)
    if type_ == "Int":
        return int(value)
    if type_ == "Float":
        return float(value[0])
    else:
        print(type_)
        return NotImplemented


class SimType(Enum):
    HYDRO_STANDARD = 0
    HYDRO_COSMOLOGICAL = 1
    POST_STANDARD = 2
    POST_COSMOLOGICAL = 3
    POST_STANDARD_ICS_COSMOLOGICAL = 4
    POST_CASCADE = 5

    def is_cosmological(self) -> bool:
        return self == SimType.HYDRO_COSMOLOGICAL or self == SimType.POST_COSMOLOGICAL


class Simulation:
    def __init__(self, folder: Path) -> None:
        self.folder = folder
        self.params = getParams(folder)

    @property  # type: ignore
    def name(self) -> str:
        return self.folder.name

    @property  # type: ignore
    def log(self) -> List[str]:
        with (self.folder / config.arepoLogFile).open("r", errors="replace") as f:
            return f.readlines()

    def __repr__(self) -> str:
        return f"Sim{self.name}"

    @property
    def outputDir(self) -> Path:
        return Path(self.folder, self.params["OutputDir"])

    @property
    def snapshots(self) -> List[Snapshot]:
        snapshotFileBase = self.params["SnapshotFileBase"]
        snapshotGlob = "{}_*.hdf5".format(snapshotFileBase)
        snapshotFiles = list(self.outputDir.glob(snapshotGlob))

        def getNumber(name: Path) -> int:
            nameRep = str(name).replace("{}_".format(snapshotFileBase), "")
            nameRep = nameRep.replace(".hdf5", "")
            nameRep = nameRep.replace(str(self.outputDir), "")
            nameRep = nameRep.replace("/", "")
            return int(nameRep)

        snapshotFiles.sort(key=getNumber)
        return [Snapshot(self, s) for s in snapshotFiles]

    def getSnapshotAtRedshift(self, redshift: pq.dimensionless_unscaled) -> Snapshot:
        snapshots = self.snapshots
        return min(snapshots, key=lambda snap: abs(redshift - self.getRedshift(snap.scale_factor)))

    def icsFile(self) -> Snapshot:
        return Snapshot(self, self.folder / "{}.hdf5".format(self.params["InitCondFile"]))

    def sources(self) -> Sources:
        return Sources(self.folder / self.params["TestSrcFile"])

    def getSlices(self, name: str) -> List[Any]:
        from bob.plots.arepoSlice import ArepoSlice

        def isCorrectSlice(filename: str) -> bool:
            return "slice" in filename and str(filename).split("_")[0] == name

        sliceFiles = [ArepoSlice(self.outputDir / f) for f in os.listdir(self.outputDir) if isCorrectSlice(f)]
        sliceFiles.sort(key=lambda s: s.path)
        return sliceFiles

    def subboxCoords(self) -> Tuple[pq.Quantity, pq.Quantity]:
        with open(Path(self.folder, self.params["SubboxCoordinatesPath"])) as f:
            lines = f.readlines()
            assert len(lines) == 1
            minX, maxX, minY, maxY, minZ, maxZ = [float(x) for x in lines[0].split(" ")]
            raise NotImplementedError("Need to get the length unit of the subbox snapshot here")
            unit = pq.m
            return (unit * np.array([minX, minY, minZ]), unit * np.array([maxX, maxY, maxZ]))

    def getCosmology(self) -> FlatLambdaCDM:
        Ob0 = self.params["OmegaBaryon"]
        Om0 = self.params["Omega0"]
        H0 = self.params["HubbleParam"] * 100.0
        return FlatLambdaCDM(H0=H0, Om0=Om0, Ob0=Ob0)

    def getRedshift(self, scale_factor: float, doAssert: bool = True) -> pq.Quantity:
        if abs(1.0 - scale_factor) < 1e-4:
            print("Found scale factor ~= 1, returning redshift 0")
            return 0.0 * pq.dimensionless_unscaled
        cosmology = self.getCosmology()
        if doAssert:
            assert self.params["ComovingIntegrationOn"]
        return z_at_value(cosmology.scale_factor, scale_factor)

    def getLookbackTime(self, scale_factor: float, doAssert: bool = True) -> float:
        cosmology = self.getCosmology()
        return cosmology.lookback_time(self.getRedshift(scale_factor, doAssert=doAssert))

    def getAge(self, scale_factor: float, doAssert: bool = True) -> float:
        cosmology = self.getCosmology()
        return cosmology.age(self.getRedshift(scale_factor, doAssert=doAssert))

    @property
    def lengthUnit(self) -> pq.Quantity:
        return self.params["UnitLength_in_cm"] * pq.cm

    @property
    def velocityUnit(self) -> pq.Quantity:
        return self.params["UnitVelocity_in_cm_per_s"] * pq.cm / pq.s

    @property
    def timeUnit(self) -> pq.Quantity:
        if not self.simType().is_cosmological():
            return self.lengthUnit / self.velocityUnit
        else:
            return pq.dimensionless_unscaled

    def simType(self) -> SimType:
        if self.params.get("simType") == "POST_STANDARD_ICS_COSMOLOGICAL":
            return SimType.POST_STANDARD_ICS_COSMOLOGICAL
        comoving = self.params["ComovingIntegrationOn"]
        hydroOn = not ("21" in self.params["runParams"])
        if comoving:
            if hydroOn:
                return SimType.HYDRO_COSMOLOGICAL
            else:
                return SimType.POST_COSMOLOGICAL
        else:
            if hydroOn:
                return SimType.HYDRO_STANDARD
            else:
                return SimType.POST_STANDARD

    def __hash__(self) -> int:
        return str(self.folder).__hash__()

    def __eq__(self, sim2: object) -> bool:
        if not isinstance(sim2, Simulation):
            return NotImplemented
        return self.folder == sim2.folder
