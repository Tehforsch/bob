import astropy.units as pq

arepoLogFile = "stdout.log"
cpuLogFile = "cpu.txt"

# Bob names
picFolder = "pics"

# Plot settings
dpi = 600

plotSerializationFileName = "plot.info"

defaultTimeUnit = pq.yr

numProcesses = 30

possibleImageSuffixes = ["png", "pdf"]

PARAMETER_FILE_NAME = "parameters.yml"
SNAPSHOT_FILE_NAME = "snapshot"
SNAPSHOTS_DIR_NAME = "snapshots"
TIME_SERIES_DIR_NAME = "time_series"

LENGTH_SCALING_IDENTIFIER = "scaling_length"
TIME_SCALING_IDENTIFIER = "scaling_time"
MASS_SCALING_IDENTIFIER = "scaling_mass"
TEMPERATURE_SCALING_IDENTIFIER = "scaling_temperature"
A_SCALING_IDENTIFIER = "scaling_a"
H_SCALING_IDENTIFIER = "scaling_h"
SCALE_FACTOR_SI_IDENTIFIER = "scale_factor_si"


def setupAstropy() -> None:
    # Make the parser recognize these
    import astropy.units as pq
    import astropy.cosmology.units as cu

    redshift = pq.def_unit("redshift", cu.redshift)
    littleh = pq.def_unit("littleh", cu.littleh)
    h = pq.def_unit("h", cu.littleh)
    pq.set_enabled_units([pq.pc, pq.kpc, pq.Mpc, pq.m, pq.cm, pq.K, pq.kg, pq.g, pq.s, pq.yr, pq.Myr, pq.kyr, pq.J, redshift, littleh, h])
