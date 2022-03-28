from typing import List
import numpy as np

import matplotlib.pyplot as plt
from bob.field import Field
from bob.snapshot import Snapshot
from bob.basicField import BasicField
from bob.simulation import Simulation
from bob.temperature import Temperature

from bob.plots.slicePlot import voronoiSlice

# import bob.plots.ionizationTime
# import bob.plots.temperaturePlots
# import bob.plots.thomsonScattering
# import bob.plots.image

basicFields = [
    BasicField("ChemicalAbundances", 0),
    BasicField("ChemicalAbundances", 1),
    BasicField("ChemicalAbundances", 2),
    BasicField("ChemicalAbundances", 3),
    BasicField("ChemicalAbundances", 4),
    BasicField("ChemicalAbundances", 5),
    BasicField("Density", None),
    BasicField("Masses", None),
    BasicField("Coordinates", None),
    BasicField("PhotonFlux", 0),
    BasicField("PhotonFlux", 1),
    BasicField("PhotonFlux", 2),
    BasicField("PhotonFlux", 3),
    BasicField("PhotonFlux", 4),
    BasicField("PhotonRates", 0),
    BasicField("PhotonRates", 1),
    BasicField("PhotonRates", 2),
    BasicField("PhotonRates", 3),
    BasicField("PhotonRates", 4),
    Temperature(),
    # CombinedAbundances(),
]


# def createVoronoiSlicePlots() -> None:
#     for basicField in basicFields:
#         for (axis, axisName) in zip([np.array([1, 0, 0]), np.array([0, 1, 0]), np.array([0, 0, 1])], ["X", "Y", "Z"]):

#             def thisSlicePlot(
#                 ax: plt.axes,
#                 sim: Simulation,
#                 snap: Snapshot,
#                 basicField: Field = basicField,
#                 axis: np.ndarray = axis,
#             ) -> None:
#                 voronoiSlice(ax, sim, snap, basicField, axis)

#             name = f"slice{axisName}{basicField.niceName}"
#             # Register plot in list
#             addSingleSnapshotPlot(name)(thisSlicePlot)


# createVoronoiSlicePlots()
