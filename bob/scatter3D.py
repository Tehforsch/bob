import matplotlib.pyplot as plt
import numpy as np


class Scatter3D:
    def __init__(self, snapshot, field, treshold):
        self.snapshot = snapshot
        self.field = field
        self.vmin = 0
        self.vmax = 1
        self.vFilterTreshold = treshold
        self.array = field.getData(snapshot)

    def plot(self, ax, **plotSettings):
        where = np.where(self.array >= self.vFilterTreshold)
        coords = [self.snapshot.coordinates[where, i] for i in range(3)]
        ax.scatter(*coords, c=self.array[where], **plotSettings)


def get3DAx():
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import

    return plt.figure().add_subplot(111, projection="3d")
