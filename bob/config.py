import numpy as np
from pathlib import Path

from bob import localConfig

cartesianIdentifier = "cartesian"

bobPath = Path(__file__).parent.resolve()


# Arepo names
binaryName = "Arepo"
srcArepoConfigFile = Path(localConfig.arepoDir, "src/arepoconfig.h")
inputFilename = "param.txt"
configFilename = "Config.sh"
miscFilename = "misc.txt"
arepoCompilationCommand = "make build -j 6"
srcFiles = ["src", "Makefile", "Makefile.systype", "prepare-config.py", "git_version.sh", "Config.sh"]
arepoConfigBuildFile = "build/arepoconfig.h"
arepoConfigSrcFile = "src/arepoconfig.h"

# Various arepo things
runTimePattern = "Code run for ([0-9.]*) seconds!"

# Bob names
substitutionFileName = "sims"
icsParamFileName = "ics"
icsFileName = "ics.hdf5"
meshRelaxedIcsFileName = "icsMR.hdf5"
jobFilename = "job"
sourceOutputFolderName = "arepo"
picFolder = "pics"
specialFolders = [picFolder]
memoizeDir = Path(Path.home(), ".bobMemoize")  # For in-file memoization to speed up plot work
initialSnapIdentifier = (
    "initialSnap"  # The name of the variable specifying the name of the file which we should copy to the output directory to run postprocessing on
)
outputFolderIdentifier = "OutputDir"
snapshotFileBaseIdentifier = "SnapshotFileBase"

# Plot settings
dpi = 600
fontSize = 9
picFileEnding = ".png"
# for prettier code
npRed = np.array([1.0, 0.0, 0.0])
npGreen = np.array([0.0, 1.0, 0.0])
npBlue = np.array([0.0, 0.0, 1.0])

# Gprof settings
gprofPartFilePattern = "gmon.out.*"
gprofSumFile = "gmon.sum"
gprofOutFile = "gprof.log"

numMeshRelaxSteps = 1

configParams = [
    "MESHRELAX",
    "NTYPES",
    "PERIODIC",
    "IMPOSE_PINNING",
    "VORONOI",
    "REGULARIZE_MESH_CM_DRIFT",
    "REGULARIZE_MESH_CM_DRIFT_USE_SOUNDSPEED",
    "REGULARIZE_MESH_FACE_ANGLE",
    "TREE_BASED_TIMESTEPS",
    "REFINEMENT_SPLIT_CELLS",
    "REFINEMENT_MERGE_CELLS",
    "SELFGRAVITY",
    "EVALPOTENTIAL",
    "DO_NOT_RANDOMIZE_DOMAINCENTER",
    "CHUNKING",
    "DOUBLEPRECISION",
    "DOUBLEPRECISION_FFTW",
    "OUTPUT_IN_DOUBLEPRECISION",
    "INPUT_IN_DOUBLEPRECISION",
    "VORONOI_DYNAMIC_UPDATE",
    "NO_MPI_IN_PLACE",
    "NO_ISEND_IRECV_IN_DOMAIN",
    "FIX_PATHSCALE_MPI_STATUS_IGNORE_BUG",
    "OUTPUT_TASK",
    "HAVE_HDF5",
    "HOST_MEMORY_REPORTING",
    "SGCHEM",
    "SGCHEM_NO_MOLECULES",
    "CHEMISTRYNETWORK",
    "JEANS_REFINEMENT",
    "CHEM_IMAGE",
    "SGCHEM_CONSTANT_ALPHAB",
    "SGCHEM_DISABLE_COMPTON_COOLING",
    "SIMPLEX",
    "SX_CHEMISTRY",
    "SX_SOURCES",
    "SX_NUM_ROT",
    "SX_HYDROGEN_ONLY",
    "SX_DISPLAY_STATS",
    "SX_DISPLAY_TIMERS",
    "SX_OUTPUT_IMAGE",
    "SX_OUTPUT_IMAGE_ALL",
    "SX_OUTPUT_FLUX",
    "SX_LOAD_BALANCE",
    "SX_DISPLAY_LOAD",
    "SX_NDIR",
    "SX_SWEEP",
    "SX_SWEEP_MOST_STRAIGHTFORWARD",
    "MAX_VARIATION_TOLERANCE",
]

# inputParameters = [
#     "InitCondFile",
#     "OutputDir",
#     "SnapshotFileBase",
#     "ICFormat",
#     "SnapFormat",
#     "TimeLimitCPU",
#     "CpuTimeBetRestartFile",
#     "ResubmitCommand",
#     "ResubmitOn",
#     "CoolingOn",
#     "StarformationOn",
#     "MaxMemSize",
#     "PeriodicBoundariesOn",
#     "ComovingIntegrationOn",
#     "TimeBegin",
#     "TimeMax",
#     "TypeOfTimestepCriterion",
#     "ErrTolIntAccuracy",
#     "CourantFac",
#     "MaxSizeTimestep",
#     "MinSizeTimestep",
#     "OutputListOn",
#     "OutputListFilename",
#     "TimeOfFirstSnapshot",
#     "TimeBetSnapshot",
#     "TimeBetStatistics",
#     "NumFilesPerSnapshot",
#     "NumFilesWrittenInParallel",
#     "Omega0",
#     "OmegaLambda",
#     "OmegaBaryon",
#     "HubbleParam",
#     "BoxSize",
#     "UnitLength_in_cm",
#     "UnitMass_in_g",
#     "UnitVelocity_in_cm_per_s",
#     "GravityConstantInternal",
#     "InitGasTemp",
#     "MinEgySpec",
#     "MinGasTemp",
#     "MinimumDensityOnStartUp",
#     "LimitUBelowThisDensity",
#     "LimitUBelowCertainDensityToThisValue",
#     "TypeOfOpeningCriterion",
#     "ErrTolTheta",
#     "ErrTolForceAcc",
#     "MultipleDomains",
#     "TopNodeFactor",
#     "ActivePartFracForNewDomainDecomp",
#     "DesNumNgb",
#     "MaxNumNgbDeviation",
#     "GasSoftFactor",
#     "SofteningComovingType0",
#     "SofteningComovingType1",
#     "SofteningComovingType2",
#     "SofteningComovingType3",
#     "SofteningComovingType4",
#     "SofteningComovingType5",
#     "SofteningMaxPhysType0",
#     "SofteningMaxPhysType1",
#     "SofteningMaxPhysType2",
#     "SofteningMaxPhysType3",
#     "SofteningMaxPhysType4",
#     "SofteningMaxPhysType5",
#     "SofteningTypeOfPartType0",
#     "SofteningTypeOfPartType1",
#     "SofteningTypeOfPartType2",
#     "SofteningTypeOfPartType3",
#     "SofteningTypeOfPartType4",
#     "SofteningTypeOfPartType5",
#     "CellMaxAngleFactor",
#     "CellShapingSpeed",
#     "ReferenceGasPartMass",
#     "TargetGasMassFactor",
#     "RefinementCriterion",
#     "DerefinementCriterion",
#     "SGChemInitH2Abund",
#     "SGChemInitHPAbund",
#     "SGChemInitDIIAbund",
#     "SGChemInitHDAbund",
#     "SGChemInitHeIIIAbund",
#     "SGChemInitCPAbund",
#     "SGChemInitCOAbund",
#     "SGChemInitCHxAbund",
#     "SGChemInitOHxAbund",
#     "SGChemInitHCOPAbund",
#     "SGChemInitHePAbund",
#     "SGChemInitMPAbund",
#     "CarbAbund",
#     "OxyAbund",
#     "MAbund",
#     "ZAtom",
#     "AtomicCoolOption",
#     "DeutAbund",
#     "H2OpacityOption",
#     "InitDustTemp",
#     "UVFieldStrength",
#     "DustToGasRatio",
#     "CosmicRayIonRate",
#     "InitRedshift",
#     "ExternalDustExtinction",
#     "H2FormEx",
#     "H2FormKin",
#     "PhotoApprox",
#     "ISRFOption",
#     "SGChemConstInitAbundances",
#     "LWBGType",
#     "LWBGStartRedsh",
#     "UnitPhotons_per_s",
#     "MinNumPhotons",
#     "TestSrcFile",
#     "sxLoadFactor",
# ]
