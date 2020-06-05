from pathlib import Path

arepoDir = "/home/toni/projects/phd/arepo"

jobParameters = {"numCores": 1}
runJobCommand = "bash"

jobTemplate = """mpirun -n {numCores} {runCommand}"""
