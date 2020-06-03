from typing import Optional, IO, Any


class BobException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class CompilationError(BobException):
    def __init__(self):
        super().__init__("Compilation error. Run with -v to see the error. I'm lazy.")
