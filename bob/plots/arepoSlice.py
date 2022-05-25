import argparse
from pathlib import Path

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
    def post(self, args: argparse.Namespace, sim: Simulation, slice_: ArepoSlice) -> Result:
        f = open(slice_.path, mode="rb")
        npix_x = np.fromfile(f, np.uint32, 1)[0]
        npix_y = np.fromfile(f, np.uint32, 1)[0]
        result = np.fromfile(f, np.float32, int(npix_x * npix_y)).reshape((int(npix_x), int(npix_y)))
        result = np.rot90(result)
        return Result(result)

    def plot(self, plt: plt.axes, result: Result) -> None:
        plt.xlabel("$x [h^{-1} \\mathrm{kpc}]$")
        plt.ylabel("$y [h^{-1} \\mathrm{kpc}]$")
        if self.slice_field == "xHP":
            vmin = 1.0e-6
            vmax = 1.0
            plt.clim(vmin, vmax)
            cbar = plt.colorbar()
            cbar.set_label("$x_{\\mathrm{H+}}$")
            plt.imshow(result.arrs[0], cmap="Reds", norm=colors.LogNorm(vmin=vmin, vmax=vmax), extent=(-17.5, 17.5, -17.5, 17.5))
        elif self.slice_field == "temp":
            vmin = 1.0e1
            vmax = 1.0e6
            plt.imshow(result.arrs[0], cmap="Reds", norm=colors.LogNorm(vmin=vmin, vmax=vmax), extent=(-17.5, 17.5, -17.5, 17.5))
            cbar = plt.colorbar()
            cbar.set_label("$T$")
        elif self.slice_field == "density":
            plt.imshow(result.arrs[0], cmap="Reds", norm=colors.LogNorm(), extent=(-17.5, 17.5, -17.5, 17.5))
            cbar = plt.colorbar()
            cbar.set_label("$\\rho$")


addToList("arepoSlice", ArepoSlicePlot())
