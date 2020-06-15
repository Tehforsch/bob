import logging
import sys
from subprocess import Popen, PIPE, check_output
from typing import Callable, Any, List, Dict, Union
from pathlib import Path


def runCommand(command: Union[str, List[str]], path: Union[str, Path], printOutput: bool = False, shell: bool = False) -> Popen:
    logging.debug("Running {}".format(command))
    if printOutput:
        process = Popen(command, cwd=path, shell=shell, stdout=sys.stdout, stderr=sys.stderr)
    else:
        process = Popen(command, cwd=path, shell=shell, stdout=PIPE, stderr=PIPE)
    process.communicate()
    return process


def checkOutput(command: Union[str, List[str]], path: Union[str, Path], printOutput: bool = False, shell: bool = False) -> bytes:
    return check_output(command, cwd=path, shell=shell)


def printArgs(func: Callable[..., Any]) -> Callable[..., Any]:
    def wrapper(*args: List[Any], **kwargs: Dict[str, Any]) -> Any:
        prettyDict = ", ".join(f"{k} = {v}" for (k, v) in kwargs)
        print(f"{func.__name__}({args}, {prettyDict}) = ", end="", flush=True)

        result = func(*args, **kwargs)
        print(f"{result}")
        return result

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
