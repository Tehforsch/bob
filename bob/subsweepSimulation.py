from typing import Any
from pathlib import Path
import yaml
from bob.subsweepSnapshot import SubsweepSnapshot
from bob.util import getFolders
from bob.baseSim import BaseSim
from bob.simType import SimType
from bob.time_series import TimeSeries
import bob.special_params
import astropy.units as pq
import astropy.cosmology.units as cu
from bob.config import setupAstropy
from bob.time_series import read_time_series
import bob.config as config
from astropy.cosmology import FlatLambdaCDM

SubsweepParameters = dict[str, Any]


def getParams(folder: Path) -> SubsweepParameters:
    filename = folder / "output" / "parameters.yml"
    with open(filename, "r") as f:
        return yaml.unsafe_load(f)


class SubsweepSimulation(BaseSim):
    def __init__(self, folder: Path) -> None:
        self.folder = folder
        self.params = getParams(folder)
        self.label = self.params.get("simLabel")

    @property
    def outputDir(self) -> Path:
        output_dir = self.params["output"].get("output_dir")
        if output_dir is None:
            name = "output"
        else:
            name = output_dir
        return Path(self.folder, name)

    @property
    def snapshotDir(self) -> Path:
        return self.outputDir / "snapshots"

    @property
    def snapshots(self) -> list[SubsweepSnapshot]:
        snapshotFolders = list(getFolders(self.snapshotDir))

        snapshotFolders.sort(key=lambda x: int(x.name))
        return [SubsweepSnapshot(s, self) for s in snapshotFolders]

    def simType(self) -> SimType:
        return SimType.POST_STANDARD

    def get_timeseries(self, name: str) -> TimeSeries:
        return read_time_series(self.outputDir / config.TIME_SERIES_DIR_NAME / f"{name}.yml", name)

    def cosmology(self) -> dict[str, float]:
        if self.params["cosmology"] is not None:
            return self.params["cosmology"]
        else:
            return {"a": 1.0, "h": 0.677}

    def scale_factor(self) -> pq.Quantity:
        return self.cosmology()["a"] * pq.dimensionless_unscaled

    def get_ionization_data(self):
        mass_av = self.get_timeseries("hydrogen_ionization_mass_average")
        time = mass_av.time
        mass_av = mass_av.value
        volume_av = self.get_timeseries("hydrogen_ionization_volume_average").value
        print("returning zero rate")
        for t, m, v in zip(time, mass_av, volume_av):
            yield t, m, v, 0.0, 0.0

    @property
    def H0(self) -> pq.Quantity:
        return self.cosmology()["h"] * pq.dimensionless_unscaled * 100.0 * (pq.km / pq.s) / pq.Mpc

    def getCosmology(self) -> FlatLambdaCDM:
        print("Assuming TNG cosmology")
        Ob0 = 0.0475007
        Om0 = 0.308983
        H0 = self.H0
        return FlatLambdaCDM(H0=H0, Om0=Om0, Ob0=Ob0)

    def boxSize(self) -> pq.Quantity:
        a = pq.def_unit("a", self.scale_factor().value * pq.dimensionless_unscaled)
        pq.add_enabled_units([a])
        boxSize = pq.Quantity(self.params["box_size"])
        boxSize = boxSize.to(pq.m, cu.with_H0(self.H0))
        # reset the units
        setupAstropy()

        return boxSize
