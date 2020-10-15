from pathlib import Path
from typing import Any, Union, List, Optional
import numpy as np
import sys


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
        s = ""
        if self.sigma is not None:
            s += "Cross sections:  " + str(self.sigma) + "\n"
        if self.energy is not None:
            s += "Excess energies: " + str(self.energy) + "\n"
        s += "x " + str(self.coord[:, 0]) + "\n"
        s += "y " + str(self.coord[:, 1]) + "\n"
        s += "z " + str(self.coord[:, 2]) + "\n"
        s += "t " + str(self.time) + "\n"
        for f in range(self.nFreq):
            s += f"sed {str(self.sed[:, f])}" + "\n"
        return s


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print(
            "Need either 1 argument ( a source file to print ) or 1 for the output file and many times 3 + 5 (the coordinates and ionization rates of the sources"
        )
    if len(sys.argv) == 2:
        inFile = sys.argv[1]
        print(Sources(Path(inFile)))
    else:
        assert (len(sys.argv) - 2) % 8 == 0
        out = Path(sys.argv[1])
        s = Sources()
        for i in range((len(sys.argv) - 2) // 8):
            inp = iter(sys.argv[2:])
            x, y, z, s1, s2, s3, s4, s5 = [float(next(inp)) for _ in range(8)]
            coord = [x, y, z]
            sed = [s1, s2, s3, s4, s5]
            s.addSource(coord, sed, [0])
            print(s)
        s.write(out)
