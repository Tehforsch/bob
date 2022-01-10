from typing import Callable, Any, Dict, List, Optional


class PostprocessingFunction:
    def __init__(self, f: Callable[..., Any], name: str) -> None:
        self.f = f
        self.name = name

    def __call__(self, *args: List[Any], **kwargs: Dict[str, Any]) -> None:
        return self.f(*args, **kwargs)


class SingleSnapshotPostprocessingFunction(PostprocessingFunction):
    pass


class PlotFunction(PostprocessingFunction):
    pass


class SingleSimPlotFunction(PostprocessingFunction):
    pass


class SingleSnapshotPlotFunction(PostprocessingFunction):
    pass


class CompareSimSingleSnapshotPlotFunction(PostprocessingFunction):
    pass


# Giving up on mypy hints on this one
def addToList(name: Optional[str], cls: Any) -> Callable[[Callable[..., Any]], Any]:
    def wrapper(f: Callable[..., Any]) -> Any:
        if name is None:
            newF = cls(f, f.__name__)
        else:
            newF = cls(f, name)
        postprocessingFunctions.append(newF)
        return newF

    return wrapper


def addPostprocessing(
    name: Optional[str],
) -> Callable[[Callable[..., Any]], PostprocessingFunction]:
    return addToList(name, PostprocessingFunction)


def addSingleSnapshotPostprocessing(
    name: Optional[str],
) -> Callable[[Callable[..., Any]], SingleSnapshotPostprocessingFunction]:
    return addToList(name, SingleSnapshotPostprocessingFunction)


def addPlot(name: Optional[str]) -> Callable[[Callable[..., Any]], PlotFunction]:
    return addToList(name, PlotFunction)


def addSingleSimPlot(
    name: Optional[str],
) -> Callable[[Callable[..., Any]], SingleSimPlotFunction]:
    return addToList(name, SingleSimPlotFunction)


def addSingleSnapshotPlot(
    name: Optional[str],
) -> Callable[[Callable[..., Any]], SingleSnapshotPlotFunction]:
    return addToList(name, SingleSnapshotPlotFunction)


def addCompareSimSingleSnapshotPlot(
    name: Optional[str],
) -> Callable[[Callable[..., Any]], CompareSimSingleSnapshotPlotFunction]:
    return addToList(name, CompareSimSingleSnapshotPlotFunction)


def checkNoDoubledNames() -> None:
    functionNames: List[str] = [f.name for f in postprocessingFunctions]
    assert len(set(functionNames)) == len(functionNames), "Two functions with the same name in postprocessing functions!"


postprocessingFunctions: List[PostprocessingFunction] = []


def functionNames() -> List[str]:
    return [f.name for f in postprocessingFunctions]
