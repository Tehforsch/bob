from pathlib import Path
from bob import config

arepoDir = "/beegfs/home/hd/hd_hd/hd_hp240/projects/phd/arepo"

jobParams = {"wallTime": "3:00:00", "jobName": "arepoTest", "logFile": "stdout.log", "maxCoresPerNode": 16, "jobLines": ""}

runJobCommand = "sbatch"

jobTemplate = """#!/bin/bash
#SBATCH --partition={partition}
#SBATCH --nodes={numNodes}
#SBATCH --ntasks-per-node={coresPerNode}
#SBATCH --time={wallTime}
#SBATCH --mem=50gb
#SBATCH --output={logFile}
#SBATCH --export=HDF5_DISABLE_VERSION_CHECK=2
{jobLines}
module load compiler/intel/16.0
module load mpi/impi/5.1.3-intel-16.0
module load numlib/gsl/2.2.1-intel-16.0
module load numlib/fftw/3.3.5-impi-5.1.3-intel-16.0
module load lib/hdf5/1.8-intel-16.0
module load devel/python_intel/3.6
startexe="mpirun {runCommand}"
exec $startexe"""
