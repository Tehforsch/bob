from pathlib import Path
import numpy as np
import h5py
import astropy.units as u
import yaml

from bob.subsweepSnapshot import read_unit_from_dataset


class TimeSeries:
    def __init__(self, path: Path, name: str) -> None:
        self.name = name
        with open(path, "r") as f:
            entries = yaml.load(f, Loader=yaml.SafeLoader)
        self.time = [entry["time"] for entry in entries]
        self.value = [entry["val"] for entry in entries]


def read_time_series(path: Path, name: str) -> TimeSeries:
    return TimeSeries(path, name)
