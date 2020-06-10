from pathlib import Path
from bob import config

arepoDir = "/beegfs/work/ws/hd_hp240-arepoTest-0/arepoSweep/arepo"

jobParameters = {"wallTime": "3:00:00", "jobName": "arepoTest", "logFile": "output.log", "maxCoresPerNode": 16}
runJobCommand = "msub"

jobTemplate = """ #MSUB -l nodes={numNodes}:ppn={coresPerNode}
#MSUB -l walltime={wallTime}
#MSUB -l pmem=4000mb
#MSUB -N {jobName}
#MSUB -o {logFile}
module load compiler/intel/16.0
module load mpi/impi/2017-intel-17.0
module load lib/hdf5/1.8-intel-16.0
module load numlib/gsl/2.2.1-intel-16.0
module load numlib/fftw/3.3.5-impi-5.1.3-intel-16.0

startexe="mpirun --bind-to core --map-by core --report-bindings {runCommand}"
cd $MOAB_SUBMITDIR
exec $startexe """
