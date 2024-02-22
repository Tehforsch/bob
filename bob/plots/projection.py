from typing import Tuple
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from scipy.spatial import cKDTree
import numpy as np
import astropy.units as pq
import astropy.cosmology.units as cu
import scipy

from bob.simulation import Simulation
from bob.subsweepSimulation import Cosmology
from bob.snapshot import Snapshot
from bob import config
from bob.postprocessingFunctions import SnapFn
from bob.result import Result
from bob.allFields import allFields, getFieldByName
from bob.field import Field
from bob.plotConfig import PlotConfig
from bob.plots.bobSlice import getDefaultCmap, Slice, readExtentConfig, getAxisByName, findOrthogonalAxes


class Projection(SnapFn):
    def __init__(self, config: PlotConfig) -> None:
        super().__init__(config)
        self.config.setDefault("field", "ionized_hydrogen_fraction", choices=[f.niceName for f in allFields])
        self.config.setDefault("xLabel", f"$x [UNIT]$")
        self.config.setDefault("yLabel", f"$y [UNIT]$")
        self.config.setDefault("vLim", None)
        self.config.setDefault("xUnit", pq.Mpc)
        self.config.setDefault("yUnit", pq.Mpc)
        self.config.setDefault("name", self.name + "_{simName}_{snapName}_{field}")
        self.config.setDefault("width", 0.1 * pq.Mpc)

    @property
    def field(self) -> Field:
        return getFieldByName(self.config["field"])

    def post(self, sim: Simulation, snap: Snapshot) -> Result:
        firstAxis, secondAxis, thirdAxis = 0, 1, 2
        result = super().post(sim, snap)
        coords = snap.coordinates
        center = snap.maxExtent * 0.5
        mask = np.where(np.abs(coords[:, thirdAxis] - center[thirdAxis]) < self.config["width"])
        data = self.field.getData(snap)[mask]
        coords = coords[mask]
        x = coords[:, firstAxis].to(self.config["xUnit"])
        y = coords[:, secondAxis].to(self.config["yUnit"])
        result.H, result.x_edges, result.y_edges, binnumber = scipy.stats.binned_statistic_2d(x, y, data)
        result.H = result.H.T * pq.dimensionless_unscaled
        result.x_edges = result.x_edges * pq.dimensionless_unscaled
        result.y_edges = result.y_edges * pq.dimensionless_unscaled
        return result

    def plot(self, plt: plt.axes, result: Result) -> None:
        fig, ax = plt.subplots(1)
        self.setupLabels(ax=ax)
        super().showTimeIfDesired(fig, result)
        X, Y = np.meshgrid(result.x_edges, result.y_edges)
        xDat = np.sum(result.H, axis=0)
        yDat = np.sum(result.H, axis=1)
        ax.pcolormesh(X, Y, result.H, norm=colors.LogNorm())
