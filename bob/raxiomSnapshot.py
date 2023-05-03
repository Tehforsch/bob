import re
import astropy.units as pq
from pathlib import Path
from bob.baseSnapshot import BaseSnapshot
import os
from bob.config import LENGTH_SCALING_IDENTIFIER, TIME_SCALING_IDENTIFIER, MASS_SCALING_IDENTIFIER, SCALE_FACTOR_SI_IDENTIFIER, SNAPSHOT_FILE_NAME, TEMPERATURE_SCALING_IDENTIFIER
from bob.util import getFolders, getFiles, printOnce
import h5py
import numpy as np


class SnapshotFileInfo:
    def __init__(self, path: Path, str_num: str, str_rank: str):
        self.path = path
        self.str_num = str_num
        self.str_rank = str_rank
        self.num = int(str_num)
        self.rank = int(str_rank)


class RaxiomSnapshot(BaseSnapshot):
    def __init__(self, path: Path, sim: "RaxiomSimulation") -> None:
        snapshot_infos = [parse_snapshot_file_name(snap_file) for snap_file in getFiles(path)]
        self.path = path
        self.filenames = [path / f for f in os.listdir(path)]
        self.name = path.name
        self.sim = sim
        self.str_num = snapshot_infos[0].str_num
        assert all(f.str_num == self.str_num for f in snapshot_infos)
        self.num = snapshot_infos[0].num
        assert all(f.num == self.num for f in snapshot_infos)
        self.lengthUnit = pq.m
        self.H0 = 65.0 * (pq.m / pq.s / pq.Mpc)
        printOnce("Returning fake value for H0")

    def hdf5FilesWithDataset(self, dataset: str) -> list[h5py.File]:
        return self.hdf5Files

    def readAttr(self, name):
        return self.hdf5Files[0].attrs[name]

    def getName(self) -> str:
        m = re.match("snap_(.*).hdf5", self.path.name)
        if m is None:
            return self.path.name.replace(".hdf5", "")
        else:
            return m.groups()[0]

    @property
    def time(self) -> pq.Quantity:
        return self.readAttr("time") * pq.s

    def position(self) -> pq.Quantity:
        return self.read_dataset("position")

    @property
    def coordinates(self) -> pq.Quantity:
        return self.position()

    def ionized_hydrogen_fraction(self) -> pq.Quantity:
        return self.read_dataset("ionized_hydrogen_fraction")

    def density(self) -> pq.Quantity:
        return self.read_dataset("density")

    def velocity(self) -> pq.Quantity:
        return self.read_dataset("velocity")

    def temperature(self) -> pq.Quantity:
        return self.read_dataset("temperature")

    def read_dataset(self, name: str) -> pq.Quantity:
        files = self.hdf5Files
        data = np.concatenate(tuple(f[name][...] for f in files))
        unit = read_unit_from_dataset(name, files[0])
        return unit * data

    @property
    def maxExtent(self):
        try:
            return np.array([1.0, 1.0, 1.0]) * pq.Quantity(self.sim.params["box_size"])
        except ValueError:
            raise NotImplementedError

    @property
    def minExtent(self):
        return np.array([0, 0, 0]) * pq.m

    def __repr__(self) -> str:
        return self.str_num


def read_unit_from_dataset(dataset_name: str, f: h5py.File) -> pq.Quantity:
    dataset = f[dataset_name]
    unit = 1.0
    unit *= pq.m ** dataset.attrs[LENGTH_SCALING_IDENTIFIER]
    unit *= pq.s ** dataset.attrs[TIME_SCALING_IDENTIFIER]
    unit *= pq.kg ** dataset.attrs[MASS_SCALING_IDENTIFIER]
    unit *= pq.K ** dataset.attrs[TEMPERATURE_SCALING_IDENTIFIER]
    return unit * dataset.attrs[SCALE_FACTOR_SI_IDENTIFIER]


def get_snapshot_paths_from_output_files(output_files: list[Path]) -> list[Path]:
    return [path for path in output_files if is_snapshot_file(path)]


def get_snapshots_from_dir(path: Path) -> list[RaxiomSnapshot]:
    snap_dirs = getFolders(path)
    return sorted([get_snapshot_from_dir(snap_dir) for snap_dir in snap_dirs], key=lambda snap: snap.num)


def parse_snapshot_file_name(path: Path) -> SnapshotFileInfo:
    snap_num = path.parent.stem
    rank_num = path.stem
    return SnapshotFileInfo(path, snap_num, rank_num)
