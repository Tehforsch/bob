from typing import Tuple, List, Optional
from abc import abstractmethod

import matplotlib.pyplot as plt
import astropy.units as pq

from bob.snapshot import Snapshot
from bob.postprocessingFunctions import MultiSetFn, PostprocessingFunction
from bob.result import Result
from bob.simulationSet import SimulationSet
from bob.simulation import Simulation
from bob.multiSet import MultiSet
from bob.util import getArrayQuantity
from bob.plotConfig import PlotConfig
from bob.snapshotFilter import SnapshotFilter
from bob.timeUtils import TimeQuantity


def addTimeArg(fn: PostprocessingFunction) -> None:
    fn.config.setDefault("time", "z", choices=["t", "z"])


def getTimeQuantityForSnap(quantity: str, sim: Simulation, snap: Snapshot) -> float:
    return snap.timeQuantity(quantity)


def getTimeQuantityFromTimeOrScaleFactor(quantity: str, sim: Simulation, snap: Snapshot, time_or_scale_factor: pq.Quantity) -> pq.Quantity:
    time = TimeQuantity(sim, time_or_scale_factor * snap.timeUnit)
    if quantity == "z":
        # I am completely lost on why but I get two different "redshift" units here that are incopatible and are causing problems, so I'll just take the value and multiply by dimensionless. I find this horrible but I dont know what else to do
        return time.redshift()
    elif quantity == "t":
        return time.time()
    else:
        raise NotImplementedError


class TimePlot(MultiSetFn):
    def __init__(self, config: PlotConfig) -> None:
        super().__init__(config)
        addTimeArg(self)
        self.config.setDefault("snapshots", None)
        if self.config["time"] == "t":
            self.config.setDefault("xUnit", "Myr")
        else:
            self.config.setDefault("xUnit", pq.dimensionless_unscaled)
        self.config.setDefault("xLabel", format(f"{self.xlabel()} [UNIT]"))
        self.config.setDefault("yLabel", format(f"{self.ylabel()} [UNIT]"))

    @abstractmethod
    def getQuantity(self, sim: Simulation, snap: Snapshot) -> pq.Quantity:
        pass

    def xlabel(self) -> str:
        return self.config["time"]

    def ylabel(self) -> str:
        return ""

    def post(self, simSets: MultiSet) -> Result:
        results = Result()
        results.data = [self.getQuantityOverTime(self.config["time"], simSet) for simSet in simSets]
        results.data = [x for x in results.data if x is not None]
        return results

    def plot(self, plt: plt.axes, result: Result) -> None:
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.set_yscale("log")
        self.setupLinePlot(ax)
        for label, color, style, result in zip(self.getLabels(), self.getColors(), self.getStyles(), result.data):
            self.addLine(result.times, result.values, label=label, color=color, **style)
        plt.legend()

    def getQuantityOverTime(self, timeQuantity: str, simSet: SimulationSet) -> Optional[Result]:
        filter_ = SnapshotFilter(self.config["snapshots"])
        snapshots = [(snap, sim) for sim in simSet for snap in filter_.get_snapshots(sim)]

        data = [getTimeAndResultForSnap(self, timeQuantity, s) for s in snapshots]
        # I had very interesting problems where doing the following would just stop
        # execution forever without any reason. I suspect some kind of memory problem,
        # but am not sure. For now, I am disabling any parallelism
        # data = runInPool(getTimeAndResultForSnap, snapshots, self, timeQuantity)
        data.sort(key=lambda x: x[0])
        result = Result()
        if len(data) == 0:
            print(f"WARNING: Found empty simSet {simSet} - skipping!")
            return None

        result.times = getArrayQuantity([x[0] for x in data])
        if type(data[0][1]) == list:
            result.values = getArrayQuantity([getArrayQuantity(x[1]) for x in data])
        else:
            result.values = getArrayQuantity([x[1] for x in data])
        return result


def getAllSnapshotsWithTime(timeQuantity: str, simSet: SimulationSet) -> List[Tuple[Snapshot, Simulation, pq.Quantity]]:
    snapshots = [(snap, sim) for sim in simSet for snap in sim.snapshots]
    snapshotsWithTime = [(snap, sim, snap.timeQuantity(timeQuantity)) for (snap, sim) in snapshots]
    snapshotsWithTime.sort(key=lambda x: x[2])
    return snapshotsWithTime


def getTimeAndResultForSnap(plot: TimePlot, timeQuantity: str, snapSim: Tuple[Snapshot, Simulation]) -> Tuple[pq.Quantity, pq.Quantity]:
    (snap, sim) = snapSim
    print(snap)
    return (snap.timeQuantity(timeQuantity), plot.getQuantity(sim, snap))
