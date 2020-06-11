from pathlib import Path

arepoDir = "/home/toni/projects/phd/arepo"

jobParams = {"numCores": 1, "logFile": "output.log", "maxCoresPerNode": 2}
runJobCommand = "bash"

jobTemplate = """mpirun -n {numCores} {runCommand} | tee {logFile}"""
