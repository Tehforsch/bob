from typing import Optional


class Field:
    def __init__(self, name: str, index: Optional[int] = None) -> None:
        self.name = name
        self.index = index

    def __repr__(self) -> str:
        if self.index is not None:
            return "{}, {}".format(self.name, self.index)
        else:
            return "{}".format(self.name)
