import argparse
from bob.simulationSet import SimulationSet
import bob.scaling
import bob.gprof


def checkNoDoubledNames() -> None:
    assert len(set(functions)) == len(functions), "Two functions with the same name in postprocessing functions!"


def main(args: argparse.Namespace, sims: SimulationSet) -> None:
    if args.functions is None:
        functionsToRun = functions
    else:
        functionsToRun = [function for function in functions if function.__name__ in args.functions]
    for postprocessingFunction in functionsToRun:
        postprocessingFunction(sims)


functions = [bob.scaling.speedup, bob.scaling.runTime, bob.gprof.runGprof]
checkNoDoubledNames()
