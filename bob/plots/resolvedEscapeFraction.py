import astropy.units as pq

from bob.plotConfig import PlotConfig
from bob.snapshot import Snapshot

from bob.plots.overHaloMass import OverHaloMass


class ResolvedEscapeFraction(OverHaloMass):
    def __init__(self, config: PlotConfig) -> None:
        config.setDefault("yUnit", 1.0 / pq.s)
        config.setDefault("statistic", "mean")
        super().__init__(config)

    def quantity(self, snap: Snapshot) -> pq.Quantity:
        # return BasicField("Density").getData(snap) * rate_136
        raise NotImplementedError()
