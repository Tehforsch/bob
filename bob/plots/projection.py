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
        config.setDefault("statistic", "mean")
        config.setDefault("name", "projection_{field}_" + config["statistic"] + "_{simName}_{snapName}")
        super().__init__(config)
        self.config.setDefault("field", "ionized_hydrogen_fraction", choices=[f.niceName for f in allFields])
        self.config.setDefault("xLabel", f"$x [UNIT]$")
        self.config.setDefault("yLabel", f"$y [UNIT]$")
        self.config.setDefault("vLim", None)
        self.config.setDefault("xUnit", pq.Mpc)
        self.config.setDefault("yUnit", pq.Mpc)
        self.config.setDefault("vUnit", pq.dimensionless_unscaled)
        self.config.setDefault("width", 0.1 * pq.Mpc)
        self.config.setDefault("position", 0.5)
        self.config.setDefault("vLim", None)
        self.config.setDefault("bins", 800)

    @property
    def field(self) -> Field:
        return getFieldByName(self.config["field"])

    def post(self, sim: Simulation, snap: Snapshot) -> Result:
        firstAxis, secondAxis, thirdAxis = 0, 1, 2
        result = super().post(sim, snap)
        coords = snap.coordinates
        center = snap.maxExtent * self.config["position"]
        mask = np.where(np.abs(coords[:, thirdAxis] - center[thirdAxis]) < self.config["width"])
        data = self.field.getData(snap)[mask].to_value(self.config["vUnit"])
        coords = coords[mask]
        x = coords[:, firstAxis].to(self.config["xUnit"])
        y = coords[:, secondAxis].to(self.config["yUnit"])
        result.H, result.x_edges, result.y_edges, binnumber = scipy.stats.binned_statistic_2d(x, y, data, bins=self.config["bins"], statistic="min")
        result.H = result.H.T * pq.dimensionless_unscaled
        result.x_edges = result.x_edges * pq.dimensionless_unscaled
        result.y_edges = result.y_edges * pq.dimensionless_unscaled
        return result

    def plot(self, plt: plt.axes, result: Result) -> None:
        fig, ax = plt.subplots(1)
        self.setupLabels(ax=ax)
        if self.config["colorscale"] is None:
            self.config["colorscale"] = getDefaultCmap(self.config["field"])
        super().showTimeIfDesired(fig, result)
        X, Y = np.meshgrid(result.x_edges, result.y_edges)
        xDat = np.sum(result.H, axis=0)
        yDat = np.sum(result.H, axis=1)
        if self.config["vLim"] is not None:
            vmin = pq.Quantity(self.config["vLim"][0]).to_value(self.config["vUnit"])
            vmax = pq.Quantity(self.config["vLim"][1]).to_value(self.config["vUnit"])
        else:
            vmin = None
            vmax = None
        res = ax.pcolormesh(X, Y, result.H, norm=colors.LogNorm(vmin=vmin, vmax=vmax),
                            cmap=self.config["colorscale"])
        cbar = fig.colorbar(res)
