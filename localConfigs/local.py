from pathlib import Path

arepoDir = "/home/toni/projects/phd/arepo"

jobParameters = {"numCores": 1, "logFile": "output.log"}
runJobCommand = "bash"

jobTemplate = """mpirun -n {numCores} {runCommand} | tee {logFile}"""
