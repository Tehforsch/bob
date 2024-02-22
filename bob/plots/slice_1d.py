import matplotlib.pyplot as plt
import astropy.units as pq
import astropy.cosmology.units as cu

from bob.simulation import Simulation
from bob.snapshot import Snapshot
from bob.postprocessingFunctions import SnapFn
from bob.result import Result
from bob.allFields import allFields, getFieldByName
from bob.field import Field
from bob.plotConfig import PlotConfig


class Slice1d(SnapFn):
    def __init__(self, config: PlotConfig) -> None:
        super().__init__(config)
        self.config.setDefault("axis", "z", choices=["x", "y", "z"])
        self.config.setDefault("field", "ionized_hydrogen_fraction", choices=[f.niceName for f in allFields])
        self.config.setDefault("xLabel", "$x [UNIT]$")
        self.config.setDefault("yLabel", "$v [UNIT]$")
        self.config.setDefault("xUnit", pq.Mpc)
        self.config.setDefault("yUnit", pq.Mpc)
        self.config.setDefault("log", True)
        self.config.setDefault("name", self.name + "_{simName}_{snapName}_{field}_{axis}")
        self.config.setDefault("yLim", [1e-6, 1e0])

    @property
    def field(self) -> Field:
        return getFieldByName(self.config["field"])

    def post(self, sim: Simulation, snap: Snapshot) -> Result:
        result = super().post(sim, snap)

        lengthUnit = snap.lengthUnit
        result.coords = snap.coordinates.to(lengthUnit, cu.with_H0(snap.H0))
        result.data = self.field.getData(snap)
        return result

    def plot(self, plt: plt.axes, result: Result) -> plt.Figure:
        fig = plt.figure()
        self.setupLinePlot(plt)
        self.showTime(fig, result)
        self.setupLabels()
        if self.config["log"]:
            plt.yscale("log")
        self.addLine(result.coords[:, 0], result.data, linestyle="", marker="o")
        return fig
