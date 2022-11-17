import numpy as np

from bob.field import Field
from bob.snapshot import Snapshot
from bob.simulation import Simulation
from bob.allFields import allFields, getFieldByName
from bob.basicField import BasicField
from bob.plots.timePlots import TimePlot

from bob.volume import Volume
from bob.plotConfig import PlotConfig


def getField(config: PlotConfig) -> Field:
    return getFieldByName(config["field"])


class MeanFieldOverTime(TimePlot):
    def __init__(self, config: PlotConfig) -> None:
        super().__init__(config)
        self.config.setDefault("field", "Temperature", choices=[f.niceName for f in allFields])
        field = self.config["field"]
        self.config.setDefault("yUnit", getField(self.config).unit)
        if self.config.get("time") == "z":
            self.config.setDefault("xLim", [40, 0])
        self.config.setDefault("average", "mass", choices=["mass", "volume"])
        avType = self.config["average"] + "Av"
        self.config.setDefault("name", f"{self.name}_{field}_{avType}", override=True)

    def xlabel(self) -> str:
        return self.config["time"]

    def ylabel(self) -> str:
        return getField(self.config).symbol

    def getQuantity(self, sim: Simulation, snap: Snapshot) -> float:
        data = getField(self.config).getData(snap)
        if self.config["average"] == "mass":
            masses = BasicField("Masses").getData(snap)
            return np.mean(data * masses) / np.mean(masses)
        else:
            volumes = Volume().getData(snap)
            return np.mean(data * volumes) / np.mean(volumes)
