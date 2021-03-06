import numpy as np
from bob.postprocessingFunctions import addSingleSnapshotPlot
import matplotlib.pyplot as plt
from bob.snapshot import Snapshot
from bob.slicePlot import voronoiSlice
from bob.scatter3D import Scatter3D
from bob.basicField import BasicField
from bob.plots.expansion import expansionInnerOuter, expansion, expansionErrorOverResolution
from bob.plots.shadowing import shadowing
from bob.plots.snapOverview import overview
from bob.simulation import Simulation
from bob.combinedField import CombinedAbundances


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
    # CombinedAbundances(),
]


def createVoronoiSlicePlots() -> None:
    for basicField in basicFields:
        for (axis, axisName) in zip([[1, 0, 0], [0, 1, 0], [0, 0, 1]], ["X", "Y", "Z"]):

            def thisSlicePlot(ax: plt.axes, sim: Simulation, snap: Snapshot, basicField: BasicField = basicField, axis: np.ndarray = axis) -> None:
                center = np.array([0.5, 0.5, 0.5]) * sim.params["BoxSize"]
                voronoiSlice(ax, sim, snap, basicField, axis)

            name = f"slice{axisName}{basicField.niceName}"
            # Register plot in list
            addSingleSnapshotPlot(name)(thisSlicePlot)


def createScatterPlots() -> None:
    for basicField in basicFields:

        def thisSlicePlot(ax: plt.axes, sim: Simulation, snap: Snapshot, basicField: BasicField = basicField) -> None:
            # center = sim.boxSize * 0.5
            Scatter3D(snap, basicField, 0).plot(ax)

        name = f"3D{basicField.niceName}"
        # Register plot in list
        addSingleSnapshotPlot(name)(thisSlicePlot)


createVoronoiSlicePlots()
createScatterPlots()
