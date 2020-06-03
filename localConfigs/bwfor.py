from pathlib import Path
import config

arepoFolder = "~/projects/arepo"

jobParameters = {"wallTime": "3:00:00", "jobName": "arepoTest", "runCommand": "./Arepo param.txt 0"}
runJobCommand = "msub"

jobTemplate = """ #MSUB -l nodes={numNodes}:ppn={processorsPerNode}
#MSUB -l walltime={wallTime}
#MSUB -l pmem=4000mb
#MSUB -N {jobName}
module load compiler/intel/16.0
module load mpi/impi/2017-intel-17.0
module load lib/hdf5/1.8-intel-16.0
module load numlib/gsl/2.2.1-intel-16.0
module load numlib/fftw/3.3.5-impi-5.1.3-intel-16.0

startexe="mpirun {runCommand}"
cd $MOAB_SUBMITDIR
exec $startexe """
