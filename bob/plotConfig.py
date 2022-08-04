from typing import Any, Dict


class PlotConfig(dict):
    def __init__(self, entries: Dict[str, Any]):
        super().__init__(entries)
        self.name_in_defaults = {k: False for k in entries}

    def setDefault(self, param: str, value: Any) -> None:
        if param not in self:
            self[param] = value
        self.name_in_defaults[param] = True

    def __getitem__(self, k: str) -> Any:
        if k == "xLabel":
            return fillInUnit(super().__getitem__(k), self["xUnit"])
        elif k == "yLabel":
            return fillInUnit(super().__getitem__(k), self["yUnit"])
        return super().__getitem__(k)

    def verifyAllSetParamsUsed(self) -> None:
        for (paramName, exists) in self.name_in_defaults.items():
            if not exists:
                raise ValueError(f"Parameter set from plot config file that does not appear in set defaults: {paramName}")


def fillInUnit(label: str, unit: str) -> str:
    if "UNIT" in label:
        return label.replace("UNIT", str(unit))
    else:
        return label
