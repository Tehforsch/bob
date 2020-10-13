from typing import Any, Tuple, Union, List, Optional, Dict, Set
import re
from pathlib import Path
from string import Formatter
import math
from abc import ABC, abstractmethod
import logging

from bob import localConfig, config


class ParamFile(ABC, dict):
    def __init__(self, filename: Path, defaults: Optional[Dict[str, Any]] = None) -> None:
        super().__init__([])
        self.filename = filename
        if defaults is not None:
            self.update(defaults)
        self.unusedParams: Set[str] = set()
        self.derivedParams: Set[str] = set()

    @abstractmethod
    def write(self) -> None:
        pass

    def setDerivedParams(self) -> None:
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
        return (groups[0], convertValue(groups[1]))

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
    def __init__(self, filename: Path, defaults: Dict[str, Any]) -> None:
        super().__init__(filename, defaults)
        for _, fieldname, _, _ in Formatter().parse(localConfig.jobTemplate):
            if fieldname:
                if not fieldname in self:
                    self[fieldname] = None
        self.unusedParams = set(
            ["numCores", "runParams", "maxCoresPerNode"]
        )  # Parameters that we might not use (numCores might be specified but coresPerNode and numNodes will be used)
        self.derivedParams = set(["numNodes", "coresPerNode", "runCommand", "partition", "runParams"])  # Parameters that are not interesting for postprocessing (we care about numCores)

    def write(self) -> None:
        for param in self:
            assert self[param] is not None, f"{param} needed for job file but not given"
        with self.filename.open("w") as f:
            f.write(localConfig.jobTemplate.format(**self))

    def setDerivedParams(self) -> None:
        self.setRunCommand()
        self.setNumCores()

    def setNumCores(self) -> None:
        if not "numCores" in self:
            self["numCores"] = 32
        if "numNodes" in self and "coresPerNode" in self:
            numCores = self["numCores"]
            if numCores <= self["maxCoresPerNode"]:
                self["coresPerNode"] = numCores
                self["numNodes"] = 1
                self["partition"] = "single"
            else:
                self["coresPerNode"] = self["maxCoresPerNode"]
                self["numNodes"] = math.ceil(numCores / self["coresPerNode"])
                self["partition"] = "multi"
                realNumCores = self["coresPerNode"] * self["numNodes"]
                if realNumCores != numCores:
                    logging.info(f"Cannot run with {numCores} cores (not divisible by max num of cores per node). Running on {realNumCores} instead.")

    def setRunCommand(self) -> None:
        runParams = self["runParams"]
        self["runCommand"] = f"./{config.binaryName} {config.inputFilename} {runParams}"


class IcsParamFile(LineParamFile):
    def __init__(self, filename: Path):
        self.commentString = "#"
        super().__init__(filename)

    def readLine(self, line: str) -> Tuple[str, Any]:
        k, v = [x.strip() for x in line.split("=")]
        return k, convertValue(v)

    def writeLine(self, param: Tuple[str, Any]) -> str:
        k, v = param
        return f"{k}={v}"
