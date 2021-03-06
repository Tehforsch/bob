class BobException(Exception):
    pass


class CompilationError(BobException):
    def __init__(self) -> None:
        super().__init__("Compilation error.")


class PostprocessingError(BobException):
    def __init__(self, s) -> None:
        super().__init__(s)
