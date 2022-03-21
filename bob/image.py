from pathlib import Path
import os
from typing import Any

import numpy as np
import matplotlib.pyplot as plt
from bob.simulation import Simulation

from bob.postprocessingFunctions import addSlicePlot


class Slice:
    def __init__(self, path: Path):
        self.path = path
        self.name = self.getName(path)

    def getName(self, path: Path) -> str:
        name = path.stem
        return name.split("_")[-1]


# Taken from arepy
def read_image(filename: Path) -> Any:
    f = open(filename, mode="rb")
    npix_x = np.fromfile(f, np.uint32, 1)[0]
    npix_y = np.fromfile(f, np.uint32, 1)[0]
    arepo_image = np.fromfile(f, np.float32, int(npix_x * npix_y)).reshape((int(npix_x), int(npix_y)))
    arepo_image = np.rot90(arepo_image)
    return arepo_image


def show_image(ax: plt.axes, sim: Simulation, slice_: Slice) -> None:
    data = read_image(slice_.path)
    plt.imshow(data)


@addSlicePlot("xHP", None)
def hpImage(ax: plt.axes, sim: Simulation, slice_: Slice) -> None:
    show_image(ax, sim, slice_)
