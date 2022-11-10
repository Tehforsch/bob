from typing import Any
from pathlib import Path
import os


jobFileTemplate = """#!/bin/bash
#SBATCH --partition={partition}
#SBATCH --nodes={numNodes}
#SBATCH --ntasks-per-node={numCoresPerNode}
#SBATCH --time={wallTime}
#SBATCH --output={logFile}
#SBATCH --export=HDF5_DISABLE_VERSION_CHECK=2
startexe="{runProgram} {executableName} {params}"""


def getJobFileContents(params: dict[str, Any]) -> str:
    return jobFileTemplate.format(**params)

def runPlotConfig(plot: Path) -> None:
    name = plot.name
    logFile = Path(name).with_suffix(".log")
    params = {
        "partition": "single",
        "numNodes": 1,
        "numCoresPerNode": 64,
        "wallTime": "2:00:00",
        "logFile": name,
        "runProgram": "/gpfs/bwfor/home/hd/hd_hd/hd_hp240/projects/cpython/python",
        "executableName": "/gpfs/bwfor/home/hd/hd_hd/hd_hp240/projects/pybob/main.py",
        "params": f"--post plot . {plot}",
    }
    jobFile = (Path(".") / plot.name).with_suffix(".job")
    with open(jobFile, "w") as f:
        f.write(getJobFileContents(params))
    os.system(f"sbatch {jobFile}")
