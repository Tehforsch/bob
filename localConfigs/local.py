from pathlib import Path

arepoDir = "/home/toni/projects/arepo"

jobParameters = {"numCores": 1}
runJobCommand = "bash"

jobTemplate = """mpirun -n {numCores} {runCommand}"""
