from pathlib import Path
import config

arepoFolder = "~/projects/arepo"

jobParameters = {"numCores": 1, "runCommand": "./Arepo param.txt 0"}
runJobCommand = "bash"

jobTemplate = """mpirun -n {numCores} {runCommand}"""
