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
        time_entries = [entry["time"] for entry in entries]
        if len(time_entries) > 0:
            if type(time_entries[0]) == dict:
                self.redshift = [u.Quantity(entry["redshift"]) for entry in time_entries]
                self.scale_factor = [u.Quantity(entry["scale_factor"]) for entry in time_entries]
                self.time = [u.Quantity(entry["time_elapsed"]) for entry in time_entries]
            else:
                self.time = [u.Quantity(entry["time"]) for entry in entries]
        self.value = [u.Quantity(entry["val"]) for entry in entries]


def read_time_series(path: Path, name: str) -> TimeSeries:
    return TimeSeries(path, name)
