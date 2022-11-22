import numpy as np
import itertools
from typing import Iterator
import matplotlib.pyplot as plt
import astropy.units as pq

from bob.postprocessingFunctions import SetFn
from bob.result import Result
from bob.plotConfig import PlotConfig
from bob.simulationSet import SimulationSet


class Entry:
    def __init__(self, name: str, time: pq.Quantity, cumTime: pq.Quantity) -> None:
        self.name = name
        self.time = time
        self.cumTime = cumTime


def parseEntry(line: str) -> Entry:
    split = line.split()
    return Entry(split[0], float(split[1]) * pq.s, float(split[3]) * pq.s)


def getBlocks(lines: list[str]) -> Iterator[list[str]]:
    linesIter = iter(lines)
    while True:
        try:
            if next(linesIter) != "":
                yield list(itertools.takewhile(lambda x: x.strip() != "", linesIter))
        except StopIteration:
            return


def parseBlock(block: list[str]) -> tuple[Entry, list[Entry]]:
    del block[0]  # header line
    totalLine = block[0]
    assert "total" in totalLine
    total = parseEntry(totalLine)
    topLevelEntries = [parseEntry(line) for line in block if line.startswith("  ") and line[2] != " "]
    return total, topLevelEntries


class RunTime(SetFn):
    def __init__(self, config: PlotConfig):
        super().__init__(config)
        self.config.setDefault("yUnit", pq.h)
        self.config.setDefault("requiredEntries", [])  # entries we should show even if theyre below the threshold

    def post(self, sims: SimulationSet) -> Result:
        THRESHOLD = 0.05
        result = Result()
        result.saveArraysWithoutUnits = True
        for sim in sims:
            contents = sim.cpuFile
            numRanks = sim.params["numCores"]
            lastBlock = list(getBlocks(contents))[-1]
            total, entries = parseBlock(lastBlock)
            shownEntries = [entry for entry in entries if entry.name in self.config["requiredEntries"] or entry.cumTime / total.cumTime >= THRESHOLD]

            def sortKey(entry: Entry) -> float:
                # make sure named entries come first in the correct order
                if entry.name in self.config["requiredEntries"]:
                    return float(self.config["requiredEntries"].index(entry.name) - len(self.config["requiredEntries"]))
                return 1.0 / entry.cumTime.to_value(self.config["yUnit"])

            shownEntries.sort(key=sortKey)
            hiddenEntries = [entry for entry in entries if entry not in shownEntries]
            shownEntries.append(Entry("rest", sum(entry.time for entry in hiddenEntries), sum(entry.cumTime for entry in hiddenEntries)))
            result.total = total.cumTime * numRanks
            result.names = np.array([entry.name for entry in shownEntries])  # this is a string np array ... kinda dumb but it works
            result.cumTimes = pq.Quantity([entry.cumTime * numRanks for entry in shownEntries])
            print(result.names, result.cumTimes)
        return result

    def plot(self, plt: plt.axes, result: Result) -> None:
        fig = plt.figure()

        ax = fig.add_subplot(111)
        ax2 = ax.twinx()
        ax.set_ylabel("T [core h]")
        ax2.set_ylabel("fraction [\\%]")
        ax.bar(result.names, result.cumTimes.to_value(self.config["yUnit"]))
        ax2.bar(result.names, result.cumTimes / result.total * 100)
        ax.set_xticklabels(result.names, rotation=45)
