import itertools
import astropy.units as pq
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
        self.header["NumPart_ThisFile"][0] = self.numParticles
        self.header["NumPart_Total"][0] = self.numParticles
        self.xi = np.array([np.linspace(0, self.header["BoxSize"], self.resolution, endpoint=False) for i in range(3)])
        self.cellsize = self.header["BoxSize"] / self.resolution
        self.xi += self.cellsize / 2
        self.xxi = np.meshgrid(*self.xi)
        # ordered as: x*ny*nz + y*nz + z
        self.coords = np.vstack([np.ravel(self.xxi[1]), np.ravel(self.xxi[0]), np.ravel(self.xxi[2])]).T
        # add a random scatter to the coordinates
        self.coords += (np.random.rand(self.numParticles, 3) - 0.5) * self.cellsize
        self.velocities = np.zeros((self.numParticles, 3)) * pq.cm / pq.s
        self.ids = np.arange(1, self.numParticles + 1)  # 1,2,3,4,5,....

    def densFromGrid(self, densityFunction: Callable[[np.ndarray], float]) -> float:
        self.volume = (self.cellsize * self.header["UnitLength_in_cm"]) ** 3 * pq.cm**3
        self.mass = np.ones(self.numParticles) * self.volume * densityFunction()
        return np.mean(self.mass / self.header["UnitMass_in_g"])

    def save(self, fileName: Path) -> None:
        with hp.File(fileName, "w") as f:
            f.create_group("Header")
            for name, value in self.header.items():
                f["Header"].attrs.create(name, value)
            f.create_group("PartType0")
            coords = self.coords * pq.cm * self.header["UnitLength_in_cm"]
            self.create_dataset(f, "Coordinates", data=coords)
            self.create_dataset(f, "Masses", self.mass)
            self.create_dataset(f, "Velocities", self.velocities)
            f["PartType0"].create_dataset("ParticleIDs", data=self.ids)
            self.create_dataset(f, "Density", self.mass / self.volume)
            kB = 1.38e-23 * pq.J / pq.K 
            proton_mass = pq.kg * 1.67e-27
            self.create_dataset(f, "InternalEnergy", np.ones(self.mass.shape) * kB * 100.0 * pq.K / proton_mass)


    def create_dataset(self, f, name, data):
        (_, (length, mass, velocity)) = get_dims(data)
        data = data.to(
            (pq.g * self.header["UnitMass_in_g"]) ** mass *
            (pq.cm * self.header["UnitLength_in_cm"]) ** length *
            ((pq.cm / pq.s) * self.header["UnitVelocity_in_cm_per_s"]) ** velocity)
        (scale, (length, mass, velocity)) = get_dims(data)
        d = f["PartType0"].create_dataset(name, data=data)
        d.attrs.create("a_scaling", 0)
        d.attrs.create("h_scaling", 0)
        d.attrs.create("length_scaling", length)
        d.attrs.create("mass_scaling", mass)
        d.attrs.create("velocity_scaling", velocity)
        d.attrs.create("to_cgs", scale)
        print(f"Creating {name} with {data.shape}")

def get_dims(data):
    # i dont like astropy units. cant get the dimension of a unit 
    for (length, mass, velocity) in itertools.product(range(-3,3), range(-3, 3), range(-3, 3)):
        t = pq.cm**length * pq.g ** mass * (pq.cm / pq.s) ** velocity
        try:
            scaling = (data.unit / t).to(pq.dimensionless_unscaled)
            return (scaling, (length, mass, velocity))
        except Exception as e:
            continue
    raise ValueError()


def createIcs(sim: Simulation, outputFile: Path, densityFunction: Callable[[np.ndarray], float], resolution: int) -> float:
    f = ICS()
    f.create(
        sim,
        resolution=resolution,
    )
    targetGasMass = f.densFromGrid(densityFunction)
    f.save(outputFile)
    return targetGasMass


def densityFunction():
    return 1.67262e-27 * pq.g / pq.cm**3


def main() -> None:
    simPath = Path(sys.argv[1])
    sim = Simulation(simPath)
    initialIcsFile = Path(sim.folder, "ics.hdf5")
    resolution = int(sys.argv[2])
    targetGasMass = createIcs(sim, initialIcsFile, densityFunction, resolution)


main()
