import logging
import sys
from subprocess import Popen, PIPE
from typing import Callable, Any, List, Dict, Union
from pathlib import Path


def runCommand(command: Union[str, List[str]], path: Path, printOutput: bool = False, shell: bool = False) -> Popen:
    logging.debug("Running {}".format(command))
    if printOutput:
        process = Popen(command, cwd=path, shell=shell, stdout=sys.stdout, stderr=sys.stderr)
    else:
        process = Popen(command, cwd=path, shell=shell, stdout=PIPE, stderr=PIPE)
    process.communicate()
    return process


def printArgs(func: Callable[..., Any]) -> Callable[..., Any]:
    def wrapper(*args: List[Any], **kwargs: Dict[str, Any]) -> Any:
        prettyDict = ", ".join(f"{k} = {v}" for (k, v) in kwargs)
        print(f"{func.__name__}({args}, {prettyDict}) = ", end="", flush=True)

        result = func(*args, **kwargs)
        print(f"{result}")
        return result

    return wrapper
