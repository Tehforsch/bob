from typing import Any, Dict, Optional, List, Set


class PlotConfig(dict):
    def __init__(self, entries: Dict[str, Any]):
        super().__init__(entries)
        self.param_names = {k: False for k in entries}
        self.required: Set[str] = set()
        self.choices: Dict[str, List[Any]] = {}

    def setDefault(self, param: str, value: Any, choices: Optional[List] = None) -> None:
        if param not in self:
            self[param] = value
        self.param_names[param] = True
        self.rememberChoices(param, choices)

    def setRequired(self, param: str, choices: Optional[List] = None) -> None:
        self.param_names[param] = True
        self.required.add(param)
        self.rememberChoices(param, choices)

    def rememberChoices(self, param: str, choices: Optional[List]) -> None:
        if choices is not None:
            self.choices[param] = choices

    def __getitem__(self, k: str) -> Any:
        if k == "xLabel":
            return fillInUnit(super().__getitem__(k), self["xUnit"])
        elif k == "yLabel":
            return fillInUnit(super().__getitem__(k), self["yUnit"])
        return super().__getitem__(k)

    def verifyAllSetParamsUsed(self) -> None:
        for (paramName, exists) in self.param_names.items():
            if not exists:
                raise ValueError(f"Parameter set from plot config file that does not appear in set defaults: {paramName}")
            if paramName in self.choices:
                value = self.choices[paramName]
                if not self[paramName] in value:
                    raise ValueError(f"Wrong parameter value for {paramName}: {value}")
        for param in self.required:
            if param not in self:
                raise ValueError(f"Required parameter not set: {param}")


def fillInUnit(label: str, unit: str) -> str:
    if "UNIT" in label:
        return label.replace("UNIT", str(unit))
    else:
        return label
