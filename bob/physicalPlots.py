import matplotlib.pyplot as plt
from bob.simulationSet import SimulationSet
from bob.slicePlot import Slice
from bob.field import Field


def expansion(ax: plt.axes, sims: SimulationSet) -> None:
    for sim in sims:
        # for snapshot in sim.snapshots:
        if len(sim.snapshots) > 0:
            snapshot = sim.snapshots[-1]
            fig, axs = ax.subplots(4)
            for (i, ax) in enumerate(axs):
                Slice(snapshot, Field("ChemicalAbundances", i), (0, 0, 0), (1, 0, 0)).plot(ax)
