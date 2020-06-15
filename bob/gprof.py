from pathlib import Path

from bob import util, config
from bob.simulationSet import SimulationSet


def runGprof(sims: SimulationSet) -> None:
    for sim in sims:
        util.checkOutput(f"gprof -s {config.binaryName} {config.gprofPartFilePattern}", path=sim.folder, shell=True)
        result = util.checkOutput(f"gprof {config.binaryName} {config.gprofSumFile}", path=sim.folder, shell=True)
        with Path(sim.folder, config.gprofOutFile).open("wb") as f:
            f.write(result)
