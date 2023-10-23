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
import polars as pl

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
        snaps = [SubsweepSnapshot(s, self) for s in snapshotFolders]
        first = snaps[0]
        for snap in snaps:
            snap.first_snapshot_this_sim = first
        return snaps

    def simType(self) -> SimType:
        if "cosmology" in self.params:
            return SimType.POST_COSMOLOGICAL
        else:
            return SimType.POST_STANDARD

    def can_get_redshift(self):
        return "cosmology" in self.params and self.params["cosmology"] != None and "params" in self.params["cosmology"]

    def get_timeseries(self, name: str) -> TimeSeries:
        return read_time_series(self.outputDir / config.TIME_SERIES_DIR_NAME / f"{name}.yml", name)

    def get_timeseries_as_dataframe(self, name: str, yUnit, tUnit=None) -> pl.DataFrame:
        series = self.get_timeseries(name)
        if "redshift" in series.__dict__:
            df = pl.DataFrame(
                {
                    "value": [val.to_value(yUnit) for val in series.value],
                    "redshift": [val.to_value(1.0) for val in series.redshift],
                }
            )
        if "time" in series.__dict__:
            df = pl.DataFrame(
                {
                    "value": [val.to_value(yUnit) for val in series.value],
                    "time": [val.to_value(tUnit) for val in series.time],
                }
            )
            print(df)
        return df

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
        redshift = mass_av.redshift
        mass_av = mass_av.value
        volume_av = self.get_timeseries("hydrogen_ionization_volume_average").value
        volume_av_rate = self.get_timeseries("weighted_photoionization_rate_volume_average").value
        for z, t, m, v in zip(redshift, time, mass_av, volume_av):
            yield z, t, m, v, volume_av_rate, 0.0

    @property
    def H0(self) -> pq.Quantity:
        return self.cosmology()["h"] * pq.dimensionless_unscaled * 100.0 * (pq.km / pq.s) / pq.Mpc

    @property
    def little_h(self) -> pq.Quantity:
        return self.cosmology()["h"]

    def getCosmology(self) -> FlatLambdaCDM:
        if "cosmology" in self.params and "params" in self.params["cosmology"]:
            return
            Ob0 = 0.0475007
            print("Assuming omega_bayron = 0.0475")
            Om0 = self["cosmology"]["params"]["omega_0"]
            H0 = self.H0
            return FlatLambdaCDM(H0=H0, Om0=Om0, Ob0=Ob0)
        else:
            print("Assuming TNG cosmology")
            Ob0 = 0.0475007
            Om0 = 0.308983
            H0 = self.H0
        return FlatLambdaCDM(H0=H0, Om0=Om0, Ob0=Ob0)

    def boxSize(self) -> pq.Quantity:
        a = pq.def_unit("a", self.scale_factor().value * pq.dimensionless_unscaled)
        cpc_over_h = pq.def_unit("cpc/h", pq.pc * self.scale_factor().value / self.little_h)
        ckpc_over_h = pq.def_unit("ckpc/h", pq.kpc * self.scale_factor().value / self.little_h)
        cMpc_over_h = pq.def_unit("cMpc/h", pq.Mpc * self.scale_factor().value / self.little_h)
        pq.add_enabled_units([a, cpc_over_h, ckpc_over_h, cMpc_over_h])
        boxSize = pq.Quantity(self.params["box_size"])
        boxSize = boxSize.to(pq.m, cu.with_H0(self.H0))
        # reset the units
        setupAstropy()

        return boxSize
