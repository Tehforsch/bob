import numpy as np
import matplotlib.pyplot as plt


class Slice:
    def __init__(self, snapshot, field, start, axis):
        self.snapshot = snapshot
        self.field = field
        self.start = start
        self.axis = axis / np.linalg.norm(axis)
        self.vmin = 0
        self.vmax = 1
        self.thickness = 0.02

    def plot(self, ax, **plotSettings):
        field = self.snapshot.getField(*self.field)
        coordinates = self.snapshot.coordinates
        ax.set_title(self.title)
        coord1, coord2, values = getSlice(field, coordinates, self.start, self.axis, self.thickness)
        print(np.mean(values))
        ax.scatter(coord1, coord2, c=values, alpha=0.2, **plotSettings, vmin=self.vmin, vmax=self.vmax)

    @property
    def title(self):
        return "{} @ {:.2f} {:.2f} {:.2f} @ {}".format(getNiceFieldName(self.field), *self.start, getNiceSnapshotName(self.snapshot))


def getSlice(array, coordinates, start, axis, thickness):
    indices = np.where(np.abs(np.dot(coordinates - start, axis)) < thickness)
    axis1, axis2 = findOrthogonalAxes(axis)
    return np.dot(coordinates[indices], axis1), np.dot(coordinates[indices], axis2), array[indices]


def getNiceSnapshotName(snapshot):
    return snapshot.filename.name


def getNiceFieldName(fieldInfo):
    return "{}{}".format(fieldInfo[0].replace("ChemicalAbundances", "Ab"), fieldInfo[1])


def findOrthogonalAxes(axis):
    xAxis = np.array([1.0, 0.0, 0.0])
    yAxis = np.array([0.0, 1.0, 0.0])
    zAxis = np.array([0.0, 0.0, 1.0])
    dotProducts = [np.abs(np.dot(axis, a)) for a in [xAxis, yAxis, zAxis]]
    mostParallel = np.argmax(dotProducts)
    mostOrthogonal = [0, 1, 2]
    mostOrthogonal.remove(mostParallel)
    basicAxis1 = [xAxis, yAxis, zAxis][mostOrthogonal[0]]
    axis1 = np.cross(basicAxis1, axis)
    axis1 = axis1 / np.linalg.norm(axis)
    axis2 = np.cross(axis1, axis)
    axis2 = axis2 / np.linalg.norm(axis)
    return axis1, axis2
