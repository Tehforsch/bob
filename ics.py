import logging
import sys
import shutil
import time
from typing import Dict, Any, Callable, Tuple
import numpy as np
import h5py as hp
from pathlib import Path
import argparse
from bob.simulationSet import SimulationSet
from bob import config
from bob.simulation import Simulation

M_sol = 1.989e33  # solar mass [g]
m_p = 1.67262178e-24  # proton mass [g]
yr = 3.15576e7  # year [s]
pc = 3.085678e18  # parsec [cm]


class ICS:
    def __init__(self) -> None:
        self.header: Dict[str, Any] = {
            "NumPart_ThisFile": [0] * 6,
            "NumPart_Total": [0] * 6,
            "NumPart_Total_HighWord": [0] * 6,
            "MassTable": [0.0] * 6,
            "Redshift": 0.0,  # redshift (for cosmological)
            "NumFilesPerSnapshot": 1,
            "Omega0": 0.0,  # for cosmological
            "OmegaLambda": 0.0,  # for cosmological
            "OmegaBaryon": 0.0,  # for cosmological
            "HubbleParam": 1.0,  # for cosmological
            "Flag_Sfr": 0,
            "Flag_Cooling": 0,
            "Flag_StellarAge": 0,
            "Flag_Metals": 0,
            "Flag_Feedback": 0,
            "Flag_DoublePrecision": 1,  # 0-single, 1-double
            "Composition_vector_length": 0,
            "UnitLength_in_cm": 1,
            "UnitMass_in_g": 1,
            "UnitVelocity_in_cm_per_s": 1,
            "Time": 0,
        }

    def create(self, sim: Simulation, resolution: int) -> None:
        # set the header information
        self.header["UnitLength_in_cm"] = float(sim.params["UnitLength_in_cm"])
        self.header["UnitMass_in_g"] = float(sim.params["UnitMass_in_g"])
        self.header["UnitVelocity_in_cm_per_s"] = float(sim.params["UnitVelocity_in_cm_per_s"])
        self.header["BoxSize"] = float(sim.params["BoxSize"])

        self.resolution = resolution
        self.numParticles = resolution**3
        # Particle types
        # 0 - gas (high-res)
        # 1 - gas (low-res)
        # 2 - DM  (high-res)
        # 3 - DM  (low-res)
        # 4 - stars
        # 5 - sinks
        self.header["NumPart_ThisFile"][0] = self.numParticles
        # self.header['NumPart_ThisFile'][3] = self.numParticles_dm
        self.header["NumPart_Total"][0] = self.numParticles
        # create coordinate bins in all directions
        self.xi = np.array([np.linspace(0, self.header["BoxSize"], self.resolution, endpoint=False) for i in range(3)])
        # size of the cell
        self.cellsize = self.header["BoxSize"] / self.resolution
        print(self.cellsize)
        # shift coordinates by half a cell
        self.xi += self.cellsize / 2
        self.xxi = np.meshgrid(*self.xi)
        # ordered as: x*ny*nz + y*nz + z
        self.coords = np.vstack([np.ravel(self.xxi[1]), np.ravel(self.xxi[0]), np.ravel(self.xxi[2])]).T
        # add a random scatter to the coordinates
        self.coords += (np.random.rand(self.numParticles, 3) - 0.5) * self.cellsize
        self.velocities = np.zeros((self.numParticles, 3))
        self.ids = np.arange(1, self.numParticles + 1)  # 1,2,3,4,5,....

    def densFromGrid(self, densityFunction: Callable[[np.ndarray], float]) -> float:
        self.volume = (self.cellsize * self.header["UnitLength_in_cm"]) ** 3  # cm^3
        self.mass = np.zeros(self.numParticles)  # g
        for c, coord in enumerate(self.coords):
            self.mass[c] = self.volume * densityFunction(coord)
        return np.mean(self.mass / self.header["UnitMass_in_g"])

    def save(self, fileName: Path) -> None:
        with hp.File(fileName, "w") as f:
            f.create_group("Header")
            for name, value in self.header.items():
                f["Header"].attrs.create(name, value)
            pt = "PartType0"
            f.create_group(pt)
            coords = self.coords  # in code units
            f[pt].create_dataset("Coordinates", data=coords)
            masses = self.mass / self.header["UnitMass_in_g"]
            f[pt].create_dataset("Masses", data=masses)
            velocities = self.velocities / self.header["UnitVelocity_in_cm_per_s"]
            f[pt].create_dataset("Velocities", data=velocities)
            f[pt].create_dataset("ParticleIDs", data=self.ids)
            f[pt].create_dataset("Density", data=self.mass / self.volume)
            f[pt].create_dataset("InternalEnergy", data=np.zeros(self.mass.shape))


def createIcs(sim: Simulation, outputFile: Path, densityFunction: Callable[[np.ndarray], float], resolution: int) -> float:
    f = ICS()
    f.create(
        sim,
        resolution=resolution,
    )  # 14 kpc  # 1 M_sol  # Myr
    targetGasMass = f.densFromGrid(densityFunction)
    print(outputFile)
    f.save(outputFile)
    return targetGasMass


def densityFunction(coord: np.ndarray) -> float:
    return 2.345e-21  # molecular h2 region test


def main() -> None:
    simPath = Path(sys.argv[1])
    sim = Simulation(simPath)
    initialIcsFile = Path(sim.folder, "ics.hdf5")
    resolution = int(sys.argv[2])
    targetGasMass = createIcs(sim, initialIcsFile, densityFunction, resolution)
    print(targetGasMass)


main()
