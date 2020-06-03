from pathlib import Path

arepoDir = "/home/toni/projects/arepo"

jobParameters = {"numCores": 1, "runCommand": "./Arepo param.txt 0"}
runJobCommand = "bash"

jobTemplate = """mpirun -n {numCores} {runCommand}"""
