from typing import List
import itertools

from pathlib import Path


def getCommonParentFolder(folders: List[Path]) -> Path:
    parts = (folder.parts for folder in folders)
    zippedParts = zip(*parts)
    commonParts = (parts[0] for parts in itertools.takewhile(lambda parts: all(part == parts[0] for part in parts), zippedParts))
    return Path(*commonParts)
