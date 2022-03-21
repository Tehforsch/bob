from typing import List
import numpy as np

from bob.postprocessingFunctions import addSingleSnapshotPlot
import matplotlib.pyplot as plt
from bob.field import Field
from bob.snapshot import Snapshot
from bob.slicePlot import voronoiSlice
from bob.scatter3D import Scatter3D
from bob.basicField import BasicField
from bob.simulation import Simulation
from bob.temperature import Temperature
import bob.ionizationTime
import bob.temperaturePlots
import bob.thomsonScattering

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


def createVoronoiSlicePlots() -> None:
    for basicField in basicFields:
        for (axis, axisName) in zip([np.array([1, 0, 0]), np.array([0, 1, 0]), np.array([0, 0, 1])], ["X", "Y", "Z"]):

            def thisSlicePlot(
                ax: plt.axes,
                sim: Simulation,
                snap: Snapshot,
                basicField: Field = basicField,
                axis: np.ndarray = axis,
            ) -> None:
                voronoiSlice(ax, sim, snap, basicField, axis)

            name = f"slice{axisName}{basicField.niceName}"
            # Register plot in list
            addSingleSnapshotPlot(name)(thisSlicePlot)


def createScatterPlots() -> None:
    for basicField in basicFields:

        def thisSlicePlot(
            ax: plt.axes,
            sim: Simulation,
            snap: Snapshot,
            basicField: Field = basicField,
        ) -> None:
            # center = sim.boxSize * 0.5
            Scatter3D(snap, basicField, 0).plot(ax)

        name = f"3D{basicField.niceName}"
        # Register plot in list
        addSingleSnapshotPlot(name)(thisSlicePlot)


createVoronoiSlicePlots()
createScatterPlots()
