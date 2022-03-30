arepoDir = "/beegfs/home/hd/hd_hd/hd_hp240/projects/arepo"

jobParams = {"numCores": 2, "logFile": "stdout.log", "maxCoresPerNode": 2}
runJobCommand = "bash"

jobTemplate = """mpirun -n {numCores} {runCommand} | tee {logFile}"""
