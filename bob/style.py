from typing import Any


class Style(dict):
    def setDefault(self, param: str, value: Any) -> None:
        if param not in self:
            self[param] = value
