from pathlib import Path

import astropy.units as pq

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from bob.simulation import Simulation
from bob.postprocessingFunctions import SliceFn
from bob.result import Result
from bob.plotConfig import PlotConfig


class ArepoSlice:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.name = self.getName(path)

    def getName(self, path: Path) -> str:
        name = path.stem
        return name.split("_")[-1]


def getUnit(field: str) -> pq.Quantity:
    if field == "xHP":
        return pq.dimensionless_unscaled
    else:
        raise ValueError("Unit for field unknown: {}".format(field))


class ArepoSlicePlot(SliceFn):
    def __init__(self, config: PlotConfig) -> None:
        super().__init__(config)
        config.setDefault("extent", None)

    # Taken from arepy
    def post(self, sim: Simulation, slice_: ArepoSlice) -> Result:
        f = open(slice_.path, mode="rb")
        result = Result()
        npix_x = np.fromfile(f, np.uint32, 1)[0]
        npix_y = np.fromfile(f, np.uint32, 1)[0]
        result.image = np.fromfile(f, np.float32, int(npix_x * npix_y)).reshape((int(npix_x), int(npix_y)))
        result.image = np.rot90(result.image) * getUnit(self.config["field"])
        result.boxSize = sim.params["BoxSize"] * sim.params["UnitLength_in_cm"] * pq.cm
        return result

    def plot(self, plt: plt.axes, result: Result) -> None:
        plt.xlabel("$x [h^{-1} \\mathrm{kpc}]$")
        plt.ylabel("$y [h^{-1} \\mathrm{kpc}]$")
        extent = (-result.boxSize, result.boxSize, -result.boxSize, result.boxSize) if self.config["extent"] is None else self.config["extent"]
        extent = [pq.Quantity(x).to_value(pq.Mpc) for x in extent]
        if self.config["field"] == "xHP":
            vmin = 1.0e-6
            vmax = 1.0
            plt.imshow(result.image, cmap="Reds", norm=colors.LogNorm(vmin=vmin, vmax=vmax), extent=extent)
            cbar = plt.colorbar()
            cbar.set_label("$x_{\\mathrm{H+}}$")
            plt.clim(vmin, vmax)
        elif self.config["field"] == "temp":
            vmin = 1.0e1
            vmax = 1.0e6
            plt.imshow(result.image, cmap="Reds", norm=colors.LogNorm(vmin=vmin, vmax=vmax), extent=extent)
            cbar = plt.colorbar()
            cbar.set_label("$T$")
        elif self.config["field"] == "density":
            plt.imshow(result.image, cmap="Reds", norm=colors.LogNorm(), extent=extent)
            cbar = plt.colorbar()
            cbar.set_label("$\\rho$")
