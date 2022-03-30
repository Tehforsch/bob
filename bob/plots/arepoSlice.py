import argparse
from pathlib import Path
import os
from typing import Any

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from bob.simulation import Simulation
from bob.postprocessingFunctions import addToList, SliceFn
from bob.result import Result


class ArepoSlice:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.name = self.getName(path)

    def getName(self, path: Path) -> str:
        name = path.stem
        return name.split("_")[-1]


class ArepoSlicePlot(SliceFn):
    def setArgs(self, subparser: argparse.ArgumentParser) -> None:
        super().setArgs(subparser)

    # Taken from arepy
    def post(self, args: argparse.Namespace, sim: Simulation, slice_: Path) -> Result:
        f = open(slice_, mode="rb")
        npix_x = np.fromfile(f, np.uint32, 1)[0]
        npix_y = np.fromfile(f, np.uint32, 1)[0]
        arepo_image = np.fromfile(f, np.float32, int(npix_x * npix_y)).reshape((int(npix_x), int(npix_y)))
        arepo_image = np.rot90(arepo_image)
        return Result([arepo_image])

    def plot(self, plt: plt.axes, result: Result) -> None:
        plt.xlabel("$x [h^{-1} \mathrm{kpc}]$")
        plt.ylabel("$y [h^{-1} \mathrm{kpc}]$")
        vmin = 1e-6
        vmax = 1
        plt.imshow(result.arrs[0], cmap="Reds", norm=colors.LogNorm(vmin=vmin, vmax=vmax), extent=(-17.5, 17.5, -17.5, 17.5))
        plt.clim(vmin, vmax)
        cbar = plt.colorbar()
        cbar.set_label("$x_{\mathrm{H+}}$")


addToList("arepoSlice", ArepoSlicePlot())
