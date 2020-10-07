from pathlib import Path

arepoDir = "/home/toni/projects/phd/arepo"

jobParams = {"numCores": 2, "logFile": "stdout.log", "maxCoresPerNode": 2}
runJobCommand = "bash"

jobTemplate = """mpirun -n {numCores} {runCommand} | tee {logFile}"""
