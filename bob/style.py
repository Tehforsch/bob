from typing import Any


class Style(dict):
    def setDefault(self, param: str, value: Any) -> None:
        if param not in self:
            self[param] = value

    def __getitem__(self, k: str) -> Any:
        if k == "xLabel":
            return fillInUnit(super().__getitem__(k), self["xUnit"])
        elif k == "yLabel":
            return fillInUnit(super().__getitem__(k), self["yUnit"])
        return super().__getitem__(k)


def fillInUnit(label: str, unit: str) -> str:
    if "UNIT" in label:
        return label.replace("UNIT", str(unit))
    else:
        return label
