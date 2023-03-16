import numpy as np
import astropy.units as pq

def getDataForRadii(data: pq.Quantity, center: pq.Quantity, coordinates: pq.Quantity, radii: pq.Quantity, mean: bool = True) -> pq.Quantity:
    result = np.zeros(radii.shape) * data.unit
    width = (radii[1] - radii[0]) / 2.0
    distanceToCenter = np.linalg.norm(coordinates - center, axis=1)
    f = np.mean if mean else np.sum
    for (i, radius) in enumerate(radii):
        result[i] = f(data[np.where((distanceToCenter > radius - width) & (distanceToCenter < radius + width))])
    return result
