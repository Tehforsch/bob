import numpy as np

from bob.field import Field
from bob.snapshot import Snapshot
from bob.simulation import Simulation
from bob.allFields import allFields, getFieldByName
from bob.basicField import BasicField
from bob.plots.timePlots import TimePlot

from bob.plotConfig import PlotConfig


def getField(config: PlotConfig) -> Field:
    return getFieldByName(config["field"])


class MeanFieldOverTime(TimePlot):
    def __init__(self, config: PlotConfig) -> None:
        config.setRequired("field", choices=[f.niceName for f in allFields])
        field = config["field"]
        config.setDefault("yUnit", getField(config).unit)
        config.setDefault("name", f"{self.name}_{field}")
        super().__init__(config)
        return

    def xlabel(self) -> str:
        return self.config["time"]

    def ylabel(self) -> str:
        return getField(self.config).symbol

    def getQuantity(self, sim: Simulation, snap: Snapshot) -> float:
        masses = BasicField("Masses").getData(snap)
        data = getField(self.config).getData(snap)
        return np.mean(data * masses) / np.mean(masses)
