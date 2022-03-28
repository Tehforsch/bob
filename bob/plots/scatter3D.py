from typing import Dict, Any

import matplotlib.pyplot as plt
import numpy as np

from bob.snapshot import Snapshot
from bob.basicField import BasicField
from bob.field import Field


class Scatter3D:
    def __init__(self, snapshot: Snapshot, field: Field, treshold: float) -> None:
        self.snapshot = snapshot
        self.field = field
        self.vmin = 0
        self.vmax = 1
        self.vFilterTreshold = treshold
        if self.field.niceName != "Coordinates":
            self.array = field.getData(snapshot)

    def plot(self, ax: plt.axes, **plotSettings: Dict[str, Any]) -> None:
        from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import

        ax = plt.figure().add_subplot(111, projection="3d")
        if self.field.niceName == "Coordinates":
            coords = [self.snapshot.coordinates[:, i] for i in range(3)]
            print(coords)
            ax.scatter(*coords, **plotSettings)
        else:
            where = np.where(self.array >= self.vFilterTreshold)
            coords = [self.snapshot.coordinates[where, i] for i in range(3)]

            ax.scatter(*coords, c=self.array[where], **plotSettings)
