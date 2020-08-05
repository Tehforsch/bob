from bob.postprocessingFunctions import addSingleSnapshotPlot
import matplotlib.pyplot as plt
from bob.snapshot import Snapshot
from bob.slicePlot import Slice
from bob.scatter3D import Scatter3D
from bob.basicField import BasicField
from bob.plots.expansion import expansionInnerOuter, expansion, expansionErrorOverResolution

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
]


def createSlicePlots() -> None:
    for basicField in basicFields:
        for (axis, axisName) in zip([[1, 0, 0], [0, 1, 0], [0, 0, 1]], ["X", "Y", "Z"]):
            center = [0.51, 0.5, 0.5]

            def thisSlicePlot(ax: plt.axes, snap: Snapshot, basicField: BasicField = basicField) -> None:
                # center = sim.boxSize * 0.5
                Slice(snap, basicField, center, axis).plot(ax)

            name = f"centerSlice{axisName}{basicField.niceName}"
            # Register plot in list
            addSingleSnapshotPlot(name)(thisSlicePlot)


def createScatterPlots() -> None:
    for basicField in basicFields:

        def thisSlicePlot(ax: plt.axes, snap: Snapshot, basicField: BasicField = basicField) -> None:
            # center = sim.boxSize * 0.5
            Scatter3D(snap, basicField, 0).plot(ax)

        name = f"scatter3D{basicField.niceName}"
        # Register plot in list
        addSingleSnapshotPlot(name)(thisSlicePlot)


createSlicePlots()
createScatterPlots()
