from pathlib import Path
from typing import Any, Union, List, Optional
import numpy as np


class Sources:
    def __init__(self, fileName: Optional[Path] = None) -> None:
        self.nSources = 0
        self.nFreq = 0
        self.nSigma = 0
        self.nEnergy = 0
        self.coord: np.ndarray = []
        self.sed: np.ndarray = []
        self.time: np.ndarray = []
        self.sigma = None
        self.energy = None

        if fileName is not None:
            self.read(fileName)

    def __len__(self) -> int:
        return self.nSources

    def __enter__(self) -> "Sources":
        return self

    def __exit__(self, type: Any, value: Any, tb: Any) -> None:
        return

    def addSource(self, coord: np.ndarray, sed: np.ndarray, time: Union[List[float], float] = None) -> None:
        if np.ndim(coord) == 1:
            coord, sed = [coord], [sed]
        time = np.zeros(len(coord)) if time is None else time
        if self.nSources == 0:
            self.coord = np.array(coord)
            self.sed = np.array(sed)
            self.time = np.array(time)
            self.nFreq = self.sed.shape[1]
        else:
            self.coord = np.append(self.coord, coord, axis=0)
            self.sed = np.append(self.sed, sed, axis=0)
            self.time = np.append(self.time, time)
        self.nSources = self.sed.shape[0]

    def read(self, fileName: Path) -> None:
        with open(fileName, "r") as f:
            nSigma, nEnergy, nSources, nFreq = np.fromfile(f, dtype="u4", count=4)
            self.nSources = nSources
            self.nFreq = nFreq
            self.nSigma = nSigma
            self.nEnergy = nEnergy
            self.sigma = np.fromfile(f, dtype="f8", count=nSigma) if nSigma > 0 else None
            self.energy = np.fromfile(f, dtype="f8", count=nEnergy) if nEnergy > 0 else None
            self.coord = np.fromfile(f, dtype="f8", count=nSources * 3).reshape((nSources, 3))
            self.sed = np.fromfile(f, dtype="f8", count=nSources * nFreq).reshape((nSources, nFreq))
            self.time = np.fromfile(f, dtype="f8", count=nSources)

    def write(self, fileName: Path) -> None:
        with open(fileName, "wb") as f:
            np.array([self.nSigma, self.nEnergy, self.nSources, self.nFreq]).astype("u4").tofile(f)
            if self.sigma is not None:
                self.sigma.astype("f8").tofile(f)
            if self.energy is not None:
                self.energy.astype("f8").tofile(f)
            np.ravel(self.coord).astype("f8").tofile(f)
            np.ravel(self.sed).astype("f8").tofile(f)
            self.time.astype("f8").tofile(f)

    def __repr__(self) -> str:
        if self.sigma is not None:
            print("Cross sections:  ", self.sigma)
        if self.energy is not None:
            print("Excess energies: ", self.energy)
        ids = slice(limit) if limit else slice(self.nSources)
        print("x", self.coord[ids, 0])
        print("y", self.coord[ids, 1])
        print("z", self.coord[ids, 2])
        print("t", self.time)
        for f in range(self.nFreq):
            print("sed %d" % f, self.sed[ids, f])
