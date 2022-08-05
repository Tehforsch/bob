import numpy as np

from bob.field import Field
from bob.snapshot import Snapshot
from bob.simulation import Simulation
from bob.allFields import allFields, getFieldByName
from bob.basicField import BasicField
from bob.plots.timePlots import TimePlot

from bob.plotConfig import PlotConfig


class MeanFieldOverTime(TimePlot):
    def __init__(self, config: PlotConfig) -> None:
        super().__init__(config)
        self.config.setRequired("field", choices=[f.niceName for f in allFields])
        self.config.setDefault("yUnit", self.field().unit)

    def xlabel(self) -> str:
        return self.config["time"]

    def ylabel(self) -> str:
        return self.field().symbol

    def field(self) -> Field:
        return getFieldByName(self.config["field"])

    def getName(self) -> str:
        field = self.config["field"]
        timeQuantity = self.config["time"]
        return f"{self.name}_{field}_{timeQuantity}"

    def getQuantity(self, sim: Simulation, snap: Snapshot) -> float:
        masses = BasicField("Masses").getData(snap)
        data = self.field().getData(snap)
        return np.mean(data * masses) / np.mean(masses)
