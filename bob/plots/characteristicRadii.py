import numpy as np
from sklearn.cluster import AgglomerativeClustering
import astropy.units as pq
import astropy.cosmology.units as cu
from scipy.spatial import cKDTree


from bob.simulation import Simulation
from bob.snapshot import Snapshot
from bob.result import Result
from bob.basicField import BasicField
from bob.plotConfig import PlotConfig
from bob.plots.timePlots import TimePlot
from bob.volume import Volume
from bob.util import getArrayQuantity
from bob.ray import getRandomRaysFrom


class CharacteristicRadiiOverTime(TimePlot):
    def __init__(self, config: PlotConfig) -> None:
        super().__init__(config)
        self.config.setDefault("yUnit", pq.kpc)
        self.config.setDefault("numRays", 10)
        self.config.setDefault("numPointsAlongRay", 1000)
        self.config.setDefault("rayLength", None)

    def getQuantity(self, sim: Simulation, snap: Snapshot) -> pq.Quantity:
        radii = self.getCharacteristicRadii(snap)
        return np.mean(radii).to(self.config["yUnit"], cu.with_H0(snap.H0))

    def getCharacteristicRadii(self, snap: Snapshot) -> pq.Quantity:
        lengthUnit = pq.kpc / cu.littleh
        coordinates = snap.coordinates.to_value(lengthUnit, cu.with_H0(snap.H0))
        hpAbundance = BasicField("ChemicalAbundances", 1).getData(snap)
        ionizedOrNot = hpAbundance < 0.5
        tree = cKDTree(coordinates)

        boxSize = (snap.sim.params["BoxSize"] * snap.sim.params["UnitLength_in_cm"] * pq.cm).to(lengthUnit, cu.with_H0(snap.H0))
        randomPositions = np.random.rand(self.config["numRays"], 3) * boxSize.to(lengthUnit, cu.with_H0(snap.H0))
        if self.config["rayLength"] is None:
            length = boxSize * 0.5
        else:
            length = self.config["rayLength"].to(lengthUnit, cu.with_H0(snap.H0))

        lengths = np.zeros(self.config["numRays"]) * lengthUnit
        for i, pos in enumerate(randomPositions):
            for ray in getRandomRaysFrom(pos, 1):
                values = ray.getValues(tree, ionizedOrNot, (0 * length, 1 * length), self.config["numPointsAlongRay"])
                islands = np.flatnonzero(np.diff(np.r_[0, values, 0]) != 0).reshape(-1, 2) - [0, 1]
                dx = (length / self.config["numPointsAlongRay"]).to(lengthUnit, cu.with_H0(snap.H0))
                if len(islands) == 0:
                    lengths[i] = 0.0 * dx
                else:
                    lengths[i] = dx * np.mean([(x[1] - x[0]) for x in islands])

        return np.mean(lengths)


def getCharacteristicRadiiReallySlowly(snap: Snapshot, distance: pq.Quantity) -> Result:
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
