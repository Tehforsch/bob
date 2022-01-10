import logging
import shutil
import time
from typing import Dict, Any, Callable, Tuple
import numpy as np
import h5py as hp
from pathlib import Path
import argparse
from bob.simulationSet import SimulationSet
from bob import config
from bob.paramFile import IcsParamFile
from bob.simulation import Simulation
from bob.icsDefaults import shadowing1, shadowing2, shadowingCenter, rType, dType

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
            "BoxSize": 1.0,  # in code units
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

        self.resolution = resolution
        self.numParticles = resolution ** 3
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

    def convertSnapWithDensityAdjusted(self, inputFile: Path, outputFile: Path, densityFunction: Callable[[np.ndarray], float]) -> None:
        shutil.copy(inputFile, outputFile)
        with hp.File(outputFile, "r") as f:
            oldMasses = f["PartType0/Masses"][:]
            coords = np.array(f["PartType0/Coordinates"][:])
            volume = np.array(f["PartType0/Masses"][:]) / np.array(f["PartType0/Density"][:])
            newMass = np.zeros(coords.shape[0])  # g
            for c, coord in enumerate(coords):
                newMass[c] = volume[c] * densityFunction(coord) / self.header["UnitMass_in_g"] * self.header["UnitLength_in_cm"] ** 3
            relDifference = np.absolute(oldMasses - newMass) / np.absolute(oldMasses)
            print("Mean density:", np.mean(newMass / volume))
            print("Variance density:", np.var(newMass / volume))
            print(f"Mean relative difference in target mass: {np.mean(relDifference)}")
        with hp.File(outputFile, "r+") as f:
            dens = np.ones(coords.shape[0]) * densityFunction(coord) * self.header["UnitLength_in_cm"] ** 3 / self.header["UnitMass_in_g"]
            f["PartType0/Density"][:] = dens
            f["PartType0/Velocities"][:] = np.zeros(coords.shape)
            f["PartType0/Masses"][:] = newMass

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


def convertIcs(sim: Simulation, inputFile: Path, outputFile: Path, densityFunction: Callable[[np.ndarray], float], resolution: int) -> None:
    print("Converting {} to {}".format(inputFile, outputFile))
    f = ICS()
    f.create(
        sim,
        resolution=resolution,
    )  # 14 kpc  # 1 M_sol  # Myr
    f.convertSnapWithDensityAdjusted(inputFile, outputFile, densityFunction)  # ,header={'BoxSize':30})
    # f.save(outputFile)


def createIcs(sim: Simulation, outputFile: Path, densityFunction: Callable[[np.ndarray], float], resolution: int) -> float:
    f = ICS()
    f.create(
        sim,
        resolution=resolution,
    )  # 14 kpc  # 1 M_sol  # Myr
    targetGasMass = f.densFromGrid(densityFunction)
    f.save(outputFile)
    return targetGasMass


def getMeshRelaxTime(meshRelaxSim: Simulation) -> float:
    return max(2 * meshRelaxSim.params["MaxSizeTimestep"], meshRelaxSim.params["TimeBetSnapshot"] * 2)


def runMeshRelax(sim: Simulation, inputFile: Path, folder: Path, densityFunction: Callable[[np.ndarray], float]) -> Tuple[Path, Simulation]:
    """Run a mesh relaxation for the simulation sim, starting from the ics in inputFile. Run the simulation in
    folder."""
    shutil.copytree(sim.folder, folder, ignore=shutil.ignore_patterns("meshRelax*", "[0-9]"))
    targetFile = Path(folder, config.icsFileName)
    shutil.copyfile(inputFile, targetFile)
    meshRelaxSim = Simulation(folder, {"runParams": sim.params["runParams"], "numCores": sim.params["numCores"]})
    meshRelaxSim.params["TimeMax"] = getMeshRelaxTime(meshRelaxSim)
    meshRelaxSim.params["InitCondFile"] = targetFile.stem
    meshRelaxSim.params["MESHRELAX"] = True
    meshRelaxSim.params.writeFiles()
    meshRelaxSim.compileArepo()
    meshRelaxSim.run(verbose=False)
    waitForMeshRelaxSim(meshRelaxSim)
    lastSnapshot = meshRelaxSim.snapshots[-1].filename
    resultFile = Path(folder, config.meshRelaxedIcsFileName)
    convertIcs(sim, lastSnapshot, resultFile, densityFunction, resolution=sim.params["resolution"])
    return resultFile, meshRelaxSim


def waitForMeshRelaxSim(sim: Simulation):
    logging.info("Waiting for sim to finish (waiting until at least 3 snapshots are written)")
    while len(sim.snapshots) < 3:
        print(
            ".",
        )
        time.sleep(5)


def getDensityFunction(name: str) -> Callable[[np.ndarray], float]:
    densityFunctions = [shadowing1, shadowing2, shadowingCenter, rType, dType]
    potentialFunctions = [f for f in densityFunctions if f.__name__ == name]
    assert len(potentialFunctions) == 1, "Invalid function name?"
    return potentialFunctions[0]


def main(args: argparse.Namespace, sims: SimulationSet) -> None:
    for sim in sims:
        paramIdentifier = "_".join("{}_{}".format(k, sim.params[k]) for k in sorted(list(sims.variedParams)))
        name = "ics_{}.hdf5".format(paramIdentifier)
        sim.icsFile = IcsParamFile(Path(sim.folder, config.icsParamFileName))
        initialIcsFile = Path(sim.folder, config.icsFileName)
        densityFunction = getDensityFunction(sim.params["densityFunction"])
        targetGasMass = createIcs(sim, initialIcsFile, densityFunction, sim.params["resolution"])
        currentIcsFile = initialIcsFile
        for i in range(config.numMeshRelaxSteps):
            logging.info("Running mesh relaxation step {}".format(i))
            sim.params["ReferenceGasPartMass"] = targetGasMass
            sim.inputFile.write()  # Update reference gas mass
            print("Running mesh relax")
            currentIcsFile, mrSim = runMeshRelax(sim, currentIcsFile, Path(sim.folder, "{}".format(i)), densityFunction)
        filename = Path(sims.folder, name)
        print(f"ReferenceGasPartMass = {targetGasMass} for {filename}")
        shutil.copyfile(mrSim.snapshots[-1].filename, filename)
