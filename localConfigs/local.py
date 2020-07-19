from pathlib import Path

arepoDir = "/home/toni/projects/phd/arepo"

jobParams = {"numCores": 1, "logFile": "stdout.log", "maxCoresPerNode": 2, "gdb": "", "wallTime": None}
runJobCommand = "bash"
defaultGdbCommand = "gdb -batch -ex run -ex bt --args"

jobTemplate = """{gdb} mpirun -n {numCores} {runCommand} | tee {logFile}"""
