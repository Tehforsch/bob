import numpy as np
from typing import Dict, Any, List, Tuple, Union, Optional
from pathlib import Path
import re
import yaml
from astropy.cosmology import FlatLambdaCDM

import bob.config as config
from bob.snapshot import Snapshot
from bob.sources import Sources, getSourcesFromParamFile


def getParams(folder: Path) -> Dict[str, Any]:
    bobParamsFile = folder / "bobParams.yaml"
    contents = yaml.load(bobParamsFile.open("r"), Loader=yaml.SafeLoader)
    result = {}
    for (k, v) in contents.items():
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


class Simulation:
    def __init__(self, folder: Path) -> None:
        self.folder = folder
        self.params = getParams(folder)
        self.replaceNumCoresInParams()

    def replaceNumCoresInParams(self) -> None:
        for line in self.log:
            match = re.match("Running with ([0-9]+) MPI tasks", line)
            if match is not None:
                self.params["numCores"] = int(match.groups()[0])
                return

        print("Failed to read number of cores from log file, using {} instead".format(self.params["numCores"]))

    @property  # type: ignore
    def name(self) -> str:
        return self.folder.name

    @property  # type: ignore
    def log(self) -> List[str]:
        with (self.folder / config.arepoLogFile).open("r") as f:
            return f.readlines()

    @property
    def runTime(self) -> Optional[float]:
        total = 0.0
        for line in self.log[::-1]:
            if self.params["SWEEP"]:
                match = re.match(config.runTimePatternSweep, line)
            else:
                match = re.match(config.runTimePatternSprai, line)
            if match is not None:
                total += float(match.groups()[0])
        if total == 0.0:
            return None
        return total

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

    def subboxCoords(self) -> Tuple[np.ndarray, np.ndarray]:
        with open(Path(self.folder, self.params["SubboxCoordinatesPath"])) as f:
            lines = f.readlines()
            assert len(lines) == 1
            minX, maxX, minY, maxY, minZ, maxZ = [float(x) for x in lines[0].split(" ")]
            return (np.array([minX, minY, minZ]), np.array([maxX, maxY, maxZ]))

    def getCosmology(self) -> FlatLambdaCDM:
        Ob0 = self.params["OmegaBaryon"]
        Om0 = self.params["Omega0"]
        H0 = self.params["HubbleParam"] * 100.0
        return FlatLambdaCDM(H0=H0, Om0=Om0, Ob0=Ob0)

    @property
    def resolution(self) -> int:
        return int(self.params["InitCondFile"].replace("ics_", ""))

    @property  # type: ignore
    def sources(self) -> Sources:
        if self.params["SX_SOURCES"] == 10:
            return Sources(Path(self.folder, self.params["TestSrcFile"]))
        elif self.params["SX_SOURCES"] == 9:
            return getSourcesFromParamFile(self)
        else:
            raise ValueError("This is not implemented yet for actual sink/star particles")

    def __hash__(self) -> int:
        return str(self.folder).__hash__()

    def __eq__(self, sim2: object) -> bool:
        if not isinstance(sim2, Simulation):
            return NotImplemented
        return self.folder == sim2.folder
