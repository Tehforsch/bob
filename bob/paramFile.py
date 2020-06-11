from typing import Any, Tuple, Union
import re
from pathlib import Path
from string import Formatter
import math
from abc import ABC, abstractmethod
import logging

from bob import localConfig, config


class ParamFile(ABC, dict):
    def __init__(self, filename: Path) -> None:
        super().__init__([])
        self.filename = filename

    @abstractmethod
    def write(self) -> None:
        pass


class LineParamFile(ParamFile):
    def __init__(self, filename: Path) -> None:
        super().__init__(filename)
        self.commentString = "#"
        with filename.open("r") as f:
            self.lines = f.readlines()
            self.update(self.readLine(self.getLineWithoutComment(line)) for line in self.lines)
            if "" in self:
                del self[""]

    def getLineWithoutComment(self, line: str) -> str:
        if self.commentString not in line:
            return line
        return line[: line.index(self.commentString)]

    def write(self) -> None:
        result = "\n".join(self.writeLine(param) for param in self.items())
        with open(self.filename, "w") as f:
            f.write(result)

    @abstractmethod
    def readLine(self, line: str) -> Tuple[str, Any]:
        pass

    @abstractmethod
    def writeLine(self, param: Tuple[str, Any]) -> str:
        pass


class InputFile(LineParamFile):
    def __init__(self, filename: Path):
        self.commentString = "%"
        super().__init__(filename)

    def readLine(self, line: str) -> Tuple[str, Any]:
        matches = re.match(r"([^\s]*)\s*([^\s]*)", line)
        if matches is None:
            return ("", "")
        groups = matches.groups()
        return (groups[0], groups[1])

    def writeLine(self, param: Tuple[str, Any]) -> str:
        k, v = param
        return f"{k}\t{v}"


class ConfigFile(LineParamFile):
    def __init__(self, filename: Path):
        self.commentString = "#"
        for param in config.configParams:
            self[param] = False  # Ensure all possible config parameters exist in the dictionary, even if they are commented out in the file
        super().__init__(filename)

    def readLine(self, line: str) -> Tuple[str, Any]:
        if "=" in line:
            k, v = line.split("=")
            return k, convertValue(v)
        identifier = line.replace("\n", "").strip()
        return (identifier, True)

    def writeLine(self, param: Tuple[str, Any]) -> str:
        k, v = param
        if isinstance(v, bool):
            return "{}{}".format("" if v else "# ", k)
        return f"{k}={v}"


def convertValue(s: str) -> Union[int, float, str]:
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return s


class JobFile(ParamFile):
    def __init__(self, filename: Path) -> None:
        super().__init__(filename)
        for _, fieldname, _, _ in Formatter().parse(localConfig.jobTemplate):
            if fieldname:
                self[fieldname] = None
        self["runParams"] = None
        self["maxCoresPerNode"] = None
        self["numCores"] = None

    def write(self) -> None:
        for param in self:
            assert self[param] is not None, f"{param} needed for job file but not given"
        with self.filename.open("w") as f:
            f.write(localConfig.jobTemplate.format(**self))

    def __getitem__(self, key: str) -> Any:
        if key == "numNodes":
            numCores = self["numCores"]
            if numCores < self["maxCoresPerNode"]:
                return 1
            else:
                return math.ceil(numCores / self["coresPerNode"])
        if key == "coresPerNode":
            numCores = self["numCores"]
            if numCores < self["maxCoresPerNode"]:
                return numCores
            else:
                return self["maxCoresPerNode"]

        return super().__getitem__(key)

    def addLocalParameters(self) -> None:
        if "jobParameters" not in dir(localConfig):
            return
        for param in localConfig.jobParameters:
            if self[param] is None:
                self[param] = localConfig.jobParameters[param]
        self.setRunCommand()
        # if "numNodes" in self and "coresPerNode" in self:
        #     numCores = self["numCores"]
        #     if numCores < self["maxCoresPerNode"]:
        #         self["coresPerNode"] = numCores
        #         self["numNodes"] = 1
        #     else:
        #         self["coresPerNode"] = self["maxCoresPerNode"]
        #         self["numNodes"] = math.ceil(numCores / self["coresPerNode"])
        #         realNumCores = self["coresPerNode"] * self["numNodes"]
        #         if realNumCores != numCores:
        #             logging.info(f"Cannot run with {numCores} cores (not divisible by max num of cores per node). Running on {realNumCores} instead.")

    def setRunCommand(self) -> None:
        runParams = self["runParams"]
        self["runCommand"] = f"./{config.binaryName} {config.inputFilename} {runParams}"
