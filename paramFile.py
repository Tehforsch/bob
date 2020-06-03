from typing import List, Dict, Any, Tuple

# from pathlib import Path
import re
import config
from util import printArgs
from pathlib import Path
from string import Formatter
import localConfig


class ParamFile(dict):
    def __init__(self, filename: Path):
        self.filename = filename
        with filename.open("r") as f:
            self.lines = f.readlines()
            self.update(self.readLine(self.getLineWithoutComment(line)) for line in self.lines)
            del self[""]

    def getLineWithoutComment(self, line: str) -> str:
        if self.commentString not in line:
            return line
        else:
            return line[: line.index(self.commentString)]

    def write(self) -> None:
        result = "\n".join(self.writeLine(param) for param in self.items())
        with open(self.filename, "w") as f:
            f.write(result)


class InputFile(ParamFile):
    def __init__(self, filename: Path):
        self.commentString = "%"
        super().__init__(filename)

    def readLine(self, line: str) -> Tuple[str, Any]:
        matches = re.match(r"([^\s]*)\s*([^\s]*)", line)
        groups = matches.groups()
        return groups

    def writeLine(self, param: Tuple[str, Any]) -> str:
        k, v = param
        return f"{k}\t{v}"


class ConfigFile(ParamFile):
    def __init__(self, filename: Path):
        self.commentString = "#"
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


def convertValue(s):
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return s


def getParamFile(filename: Path) -> ParamFile:
    if config.inputFilename == filename.name:
        return InputFile(filename)
    if config.configFilename == filename.name:
        return ConfigFile(filename)
    if config.jobFilename == filename.name:
        return JobFile(filename)


class JobFile(ParamFile):
    def __init__(self, filename: Path) -> None:
        self.filename = filename
        for _, fieldname, _, _ in Formatter().parse(localConfig.jobTemplate):
            if fieldname:
                self[fieldname] = None

    def write(self) -> None:
        for param in self:
            assert self[param] != None, f"{param} needed for job file but not given"
        with self.filename.open("w") as f:
            f.write(localConfig.jobTemplate.format(**self))

    def addLocalParameters(self):
        if not "jobParameters" in dir(localConfig):
            return
        for param in localConfig.jobParameters:
            self[param] = localConfig.jobParameters[param]
