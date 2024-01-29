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
from contextlib import contextmanager


SubsweepParameters = dict[str, Any]


def getParams(folder: Path) -> SubsweepParameters:
    filename = folder / "output" / "parameters.yml"
    with open(filename, "r") as f:
        return yaml.unsafe_load(f)


class Cosmology(dict):
    def __init__(self, vals):
        super().__init__(vals)

    @contextmanager
    def unit_context(self):
        a = pq.def_unit("a", self["a"] * pq.dimensionless_unscaled)
        cpc_over_h = pq.def_unit("cpc/h", pq.pc * self["a"] / self["h"])
        ckpc_over_h = pq.def_unit("ckpc/h", pq.kpc * self["a"] / self["h"])
        cMpc_over_h = pq.def_unit("cMpc/h", pq.Mpc * self["a"] / self["h"])
        h = pq.def_unit("h", self["h"])
        cpc = pq.def_unit("cpc", pq.pc * self["a"])
        ckpc = pq.def_unit("ckpc", pq.kpc * self["a"])
        cMpc = pq.def_unit("cMpc", pq.Mpc * self["a"])
        pq.add_enabled_units([a, cpc_over_h, ckpc_over_h, cMpc_over_h, cpc, ckpc, cMpc, h])
        try:
            yield ()
        finally:
            # reset the units
            setupAstropy()


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

    def get_performance_data(self) -> dict:
        path = self.outputDir / "performance.yml"
        with open(path, "r") as f:
            return yaml.load(f, Loader=yaml.SafeLoader)

    def get_timeseries(self, name: str) -> TimeSeries:
        return read_time_series(self.outputDir / config.TIME_SERIES_DIR_NAME / f"{name}.yml", name)

    def get_timeseries_as_dataframe(self, name: str, yUnit, tUnit=None, filterTrailingValues=False) -> pl.DataFrame:
        series = self.get_timeseries(name)
        df = pl.DataFrame(
            {
                "value": [val.to_value(yUnit) for val in series.value],
            }
        )
        if "redshift" in series.__dict__:
            df = df.with_columns(pl.Series(name="redshift", values=[val.to_value(1.0) for val in series.redshift]))
        if "time" in series.__dict__:
            df = df.with_columns(pl.Series(name="time", values=[val.to_value(tUnit) for val in series.time]))
        if filterTrailingValues:
            lastSnapshotTime = max(snap.time for snap in self.snapshots).to_value(tUnit)
            df = df.filter(pl.col("time") <= lastSnapshotTime)
        return df

    def cosmology(self) -> Cosmology:
        if self.params["cosmology"] is not None:
            return Cosmology(self.params["cosmology"])
        else:
            return Cosmology({"a": 1.0, "h": 0.677})

    def scale_factor(self) -> pq.Quantity:
        return self.cosmology()["a"] * pq.dimensionless_unscaled

    def get_ionization_data(self):
        mass_av = self.get_timeseries("hydrogen_ionization_mass_average")
        time = mass_av.time
        redshift = mass_av.redshift
        mass_av = mass_av.value
        volume_av = self.get_timeseries("hydrogen_ionization_volume_average").value
        volume_av_rate = self.get_timeseries("weighted_photoionization_rate_volume_average").value
        for z, t, m, v, r in zip(redshift, time, mass_av, volume_av, volume_av_rate):
            yield z, t, m, v, r, 0.0

    @property
    def H0(self) -> pq.Quantity:
        return self.cosmology()["h"] * pq.dimensionless_unscaled * 100.0 * (pq.km / pq.s) / pq.Mpc

    @property
    def little_h(self) -> pq.Quantity:
        return self.cosmology()["h"]

    def getCosmology(self) -> FlatLambdaCDM:
        if "cosmology" in self.params and "params" in self.params["cosmology"]:
            Ob0 = 0.0486
            print("Assuming omega_bayron = 0.0486")
            Om0 = self.cosmology()["params"]["omega_0"]
            H0 = self.H0
            return FlatLambdaCDM(H0=H0, Om0=Om0, Ob0=Ob0)
        else:
            print("Assuming TNG cosmology")
            Ob0 = 0.0475007
            Om0 = 0.308983
            H0 = self.H0
        return FlatLambdaCDM(H0=H0, Om0=Om0, Ob0=Ob0)

    def convertComovingUnit(self, u, v):
        with self.comovingUnits() as _:
            u = pq.Unit(u)
            v = pq.Quantity(v)
            res = v.to(u, cu.with_H0(self.H0))
        return res

    def boxSizeForUnit(self, u) -> pq.Quantity:
        return self.convertComovingUnit(u, self.params["box_size"])

    def boxSize(self) -> pq.Quantity:
        return self.boxSizeForUnit(pq.m)

    def comovingBoxSize(self) -> pq.Quantity:
        return self.boxSizeForUnit("ckpc/h")

    @contextmanager
    def comovingUnits(self):
        with self.cosmology().unit_context() as u:
            try:
                yield u
            finally:
                pass
