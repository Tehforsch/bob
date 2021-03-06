import logging
from typing import Dict, Any, List, Iterator, Set, Optional
from collections.abc import MutableMapping

from bob.paramFile import ParamFile


class Params(MutableMapping):
    def __init__(self, files: List[ParamFile]) -> None:
        self.files = files

    def setDerivedParams(self) -> None:
        for paramFile in self.files:
            paramFile.setDerivedParams()

    def getDerivedParams(self) -> Set[str]:
        return set.union(*(f.derivedParams for f in self.files))

    def writeFiles(self) -> None:
        for paramFile in self.files:
            paramFile.write()

    def getParamFileWithParameter(self, k: str) -> Optional[ParamFile]:
        paramFilesWithThisParameter = [paramFile for paramFile in self.files if k in paramFile or k in paramFile.unusedParams]
        if len(paramFilesWithThisParameter) == 0:
            logging.error(f"No file contains this parameter: {k}")
            return None
        assert len(paramFilesWithThisParameter) <= 1, f"Multiple files contain this parameter: {k}: {paramFilesWithThisParameter}"
        return paramFilesWithThisParameter[0]

    def __getitem__(self, k: str) -> Any:
        return self.getParamFileWithParameter(k)[k]

    def __contains__(self, k: str) -> Any:
        return self.getParamFileWithParameter(k) != None

    def __setitem__(self, k: str, v: Any) -> None:
        f = self.getParamFileWithParameter(k)
        if f is None:
            logging.error("Invalid parameter: {} (might be fine though)".format(k))
        else:
            f[k] = v

    def __iter__(self) -> Iterator[Any]:
        return iter([k for f in self.files for k in f.keys()])

    def __delitem__(self, k: Any) -> None:
        del self.getParamFileWithParameter(k)[k]

    def __len__(self) -> int:
        return sum(len(f) for f in self.files)

    def updateParams(self, substitutions: Dict[Any, Any]) -> None:
        for (k, v) in substitutions.items():
            self[k] = v
