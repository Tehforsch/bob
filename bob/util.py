from typing import Callable, Any, List, Dict, Union, Iterable
import itertools
import logging
import sys
from subprocess import Popen, PIPE, check_output
from math import isclose

import numpy as np
from pathlib import Path
import quantities as pq
import pickle

from bob import config


def fileMemoize(func: Callable[..., Any]) -> Callable[..., Any]:
    def wrapper(*args: List[Any], **kwargs: Dict[Any, Any]) -> Any:
        callName = func.__name__ + str((args, tuple(kwargs.items())).__hash__())
        if not config.memoizeDir.is_dir():
            config.memoizeDir.mkdir()

        resultFile = Path(config.memoizeDir, callName)
        if resultFile.is_file():
            result = pickle.load(resultFile.open("rb"))
            logging.info(f"REUSING MEMOIZED RESULT FOR {func.__name__}")
            return result
        else:
            result = func(*args, **kwargs)
            pickle.dump(result, resultFile.open("wb"))
            return result

    return wrapper


def unitNpArray(values: List[pq.quantity.Quantity]) -> np.ndarray:
    assert len(values) > 0, "What unit am I supposed to turn this empty array into?"
    units = values[0].units
    assert all(units == v.units for v in values[1:]), "Inconsistent unit in list"
    return units * np.array([float(x) for x in values])


def runCommand(
    command: Union[str, List[str]],
    path: Union[str, Path],
    printOutput: bool = False,
    shell: bool = False,
) -> Popen:
    logging.debug("Running {}".format(command))
    if printOutput:
        process = Popen(command, cwd=path, shell=shell, stdout=sys.stdout, stderr=sys.stderr)
    else:
        process = Popen(command, cwd=path, shell=shell, stdout=PIPE, stderr=PIPE)
    process.communicate()
    return process


def checkOutput(
    command: Union[str, List[str]],
    path: Union[str, Path],
    printOutput: bool = False,
    shell: bool = False,
) -> bytes:
    return check_output(command, cwd=path, shell=shell)


def printArgs(func: Callable[..., Any]) -> Callable[..., Any]:
    def wrapper(*args: List[Any], **kwargs: Dict[str, Any]) -> Any:
        prettyDict = ", ".join(f"{k} = {v}" for (k, v) in kwargs.items())
        print(f"{func.__name__}({args}, {prettyDict}) = ", end="", flush=True)

        result = func(*args, **kwargs)
        print(f"{result}")
        return result

    return wrapper


def toList(func: Callable[..., Iterable[Any]]) -> Callable[..., List[Any]]:
    def wrapper(*args: List[Any], **kwargs: Dict[str, Any]) -> Any:
        result = func(*args, **kwargs)
        return list(result)

    return wrapper


def memoize(func: Callable[..., Any]) -> Callable[..., Any]:
    cache: Dict[Any, Any] = {}

    def wrapper(*args: List[Any], **kwargs: Dict[str, Any]) -> Any:
        key = str(args) + str(kwargs)
        if key in cache:
            return cache[key]
        result = func(*args, **kwargs)
        cache[key] = result
        return result

    return wrapper


def getNiceTimeUnitName(value: float) -> str:
    if isclose(value, 31557605363103.023):
        return "Myr"

    assert False, f"Found no nice name for time unit with value {value}"


def getNiceParamName(k: str, v: Any) -> str:
    if k == "SWEEP":
        return "Sweep" if v else "SPRAI"
    if k == "ReferenceGasPartMass":
        return ""
    if k == "InitCondFile":
        return "${}^3$".format(v.replace("ics_", ""))
    return "{}: {}".format(k, v)


def getCommonParentFolder(folders: List[Path]) -> Path:
    parts = (folder.parts for folder in folders)
    zippedParts = zip(*parts)
    commonParts = (parts[0] for parts in itertools.takewhile(lambda parts: all(part == parts[0] for part in parts), zippedParts))
    return Path(*commonParts)
