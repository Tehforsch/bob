from bob.field import Field
from bob.basicField import BasicField
from bob.snapshot import Snapshot

import numpy as np
import astropy.units as pq
import astropy.cosmology.units as cu
from scipy.spatial import cKDTree


class SourceField(Field):
    def getData(self, snapshot: Snapshot) -> np.ndarray:
        coords = BasicField("Coordinates", partType=0).getData(snapshot)
        tree = cKDTree(coords)
        source = np.zeros(coords.shape[0]) / pq.s
        type_ = snapshot.sim.params["SX_SOURCES"]
        if type_ == 4:
            try:
                starMasses = BasicField("Masses", partType=4).getData(snapshot)
                starCoords = BasicField("Coordinates", partType=4).getData(snapshot)
            except KeyError:
                # Might just be that there are no stars at this point
                return source
            cellIndices = tree.query(starCoords)[1]
            print("Using ridiculous approximation for source strength. To do this properly, write out stellar age and take SourceFactor into account")
            source[cellIndices] = 1e40 / pq.s * starMasses.to_value(pq.Msun, cu.with_H0(snapshot.H0))
        elif type_ == 10:
            sources = snapshot.sim.sources()
            starCoords = sources.getCoords(snapshot.sim)
            cellIndices = tree.query(starCoords)[1]
            luminosity = sources.get136IonisationRate(snapshot.sim)
            source[cellIndices] = luminosity
        else:
            raise NotImplementedError("currently, source field is only implemented for star particles and test sources")
        return source

    @property
    def niceName(self) -> str:
        return "Sources"

    @property
    def symbol(self) -> str:
        return "Sources"

    @property
    def unit(self) -> pq.Quantity:
        return 1.0 / pq.s
