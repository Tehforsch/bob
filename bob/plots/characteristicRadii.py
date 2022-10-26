import numpy as np
from sklearn.cluster import AgglomerativeClustering
import astropy.units as pq
import astropy.cosmology.units as cu

from bob.simulation import Simulation
from bob.snapshot import Snapshot
from bob.result import Result
from bob.basicField import BasicField
from bob.plotConfig import PlotConfig
from bob.plots.timePlots import TimePlot
from bob.volume import Volume
from bob.util import getArrayQuantity


class CharacteristicRadiiOverTime(TimePlot):
    def __init__(self, config: PlotConfig) -> None:
        super().__init__(config)
        self.config.setDefault("distance", 100.0 * pq.kpc)
        self.config.setDefault("yUnit", pq.kpc)

    def getQuantity(self, sim: Simulation, snap: Snapshot) -> pq.Quantity:
        radii = getCharacteristicRadii(snap, self.config["distance"]).radii
        return np.mean(radii)


def getCharacteristicRadii(snap: Snapshot, distance: pq.Quantity) -> Result:
    lengthUnit = pq.kpc / cu.littleh
    coordinates = snap.coordinates.to_value(lengthUnit, cu.with_H0(snap.H0))
    volumes = Volume().getData(snap)
    distance = distance.to_value(lengthUnit, cu.with_H0(snap.H0))
    hpAbundance = BasicField("ChemicalAbundances", 1).getData(snap)
    ionizedCoordinates = coordinates[np.where(hpAbundance > 0.5)]
    clustering = AgglomerativeClustering(distance_threshold=distance, n_clusters=None, linkage="single")
    clustering.fit(ionizedCoordinates)
    print(f"Found {clustering.n_clusters_} clusters for snap: {snap}.")

    def clusterRadius(i: int) -> pq.Quantity:
        totalVolume = np.sum(volumes[np.where(clustering.labels_ == i)])
        return 3.0 / (4.0 * np.pi) * np.cbrt(totalVolume)

    result = Result()
    result.radii = getArrayQuantity([clusterRadius(i) for i in range(clustering.n_clusters_)])
    return result
