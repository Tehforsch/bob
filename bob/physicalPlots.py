import matplotlib.pyplot as plt
import numpy as np
from bob.simulationSet import SimulationSet
from bob.snapshot import Snapshot
from bob.slicePlot import Slice
from bob.basicField import BasicField
from bob.field import Field
from bob.postprocessingFunctions import addPlot, addSingleSnapshotPlot

basicFields = [
    BasicField("ChemicalAbundances", 0),
    BasicField("ChemicalAbundances", 1),
    BasicField("ChemicalAbundances", 2),
    BasicField("ChemicalAbundances", 3),
    BasicField("ChemicalAbundances", 4),
    BasicField("ChemicalAbundances", 5),
    BasicField("Density", None),
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


@addPlot(None)
def expansion(ax: plt.axes, sims: SimulationSet) -> None:
    for sim in sims:
        # for snapshot in sim.snapshots:
        if len(sim.snapshots) > 0:
            snapshot = sim.snapshots[-1]
            fig, axs = ax.subplots(4)
            for (i, ax_) in enumerate(axs):
                Slice(snapshot, BasicField("ChemicalAbundances", i), (0.5, 0.5, 0.5), (1, 0, 0)).plot(ax_)


slicePlots = []


def createSlicePlots() -> None:
    for basicField in basicFields:
        for (axis, axisName) in zip([[1, 0, 0], [0, 1, 0], [0, 0, 1]], ["X", "Y", "Z"]):

            center = [0.5, 0.5, 0.5]

            def thisSlicePlot(ax: plt.axes, snap: Snapshot, basicField=basicField) -> None:
                # center = sim.boxSize * 0.5
                print(basicField)
                Slice(snap, basicField, center, axis).plot(ax)

            name = f"centerSlice{axisName}{basicField.niceName}"
            thisSlicePlot.__name__ = name
            slicePlots.append(thisSlicePlot)
            # Register plot in list
            addSingleSnapshotPlot(name)(slicePlots[-1])


createSlicePlots()
