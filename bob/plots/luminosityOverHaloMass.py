import astropy.units as pq

from bob.plotConfig import PlotConfig
from bob.sourceField import SourceField
from bob.snapshot import Snapshot

from bob.plots.overHaloMass import OverHaloMass


class LuminosityOverHaloMass(OverHaloMass):
    def __init__(self, config: PlotConfig) -> None:
        config.setDefault("yUnit", 1.0 / pq.s)
        config.setDefault("yLabel", "$L_{\\star} [1/s]$")
        config.setDefault("statistic", "sum")
        super().__init__(config)

    def quantity(self, snap: Snapshot) -> pq.Quantity:
        return SourceField().getData(snap)
