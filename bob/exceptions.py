class BobException(Exception):
    pass


class CompilationError(BobException):
    def __init__(self) -> None:
        super().__init__("Compilation error. Run with -v to see the error. I'm lazy.")
