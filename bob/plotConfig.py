import astropy.units as pq
from typing import Any, Dict, Optional, List, Set


class PlotConfig(dict):
    def __init__(self, entries: Dict[str, Any]):
        super().__init__(entries)
        self.unmentioned_params = set(entries.keys())
        self.required: Set[str] = set()
        self.choices: Dict[str, List[Any]] = {}
        self.defaults: Dict[str, Any] = {}

    def setDefault(self, param: str, value: Any, choices: Optional[List] = None, override: bool = False) -> None:
        if not override and param in self.defaults:
            return
        self.defaults[param] = value
        self.paramMentioned(param)
        self.rememberChoices(param, choices)
        if type(value) == pq.Quantity:
            if param in self:
                self[param] = pq.Quantity(self[param])

    def setRequired(self, param: str, choices: Optional[List] = None) -> None:
        self.paramMentioned(param)
        self.required.add(param)
        self.rememberChoices(param, choices)

    def paramMentioned(self, param: str) -> None:
        if param in self.unmentioned_params:
            self.unmentioned_params.remove(param)

    def rememberChoices(self, param: str, choices: Optional[List]) -> None:
        if choices is not None:
            self.choices[param] = choices

    def __getitem__(self, k: str) -> Any:
        if k in self:
            return super().__getitem__(k)
        else:
            return self.defaults[k]

    def verify(self) -> None:
        for param in self.unmentioned_params:
            print("unused: ", param)
        for param in self.required:
            if param not in self:
                raise ValueError(f"Required parameter not set: {param}")
        for param, choices in self.choices.items():
            if not self[param] in choices:
                value = self[param]
                raise ValueError(f"Wrong parameter value for {param}: {value}")
