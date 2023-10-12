from typing import List, Type

from bob.postprocessingFunctions import PostprocessingFunction
from bob.plots.sliceWithStarParticles import SliceWithStarParticles
from bob.plots.ionization import Ionization
from bob.plots.ionizationRate import IonizationRate
from bob.plots.ionizationTime import IonizationTime
from bob.plots.ionizationBinned import IonizationBinned
from bob.plots.ionizationLevel import IonizationLevel
from bob.plots.thomsonScattering import ThomsonScattering
from bob.plots.arepoSlice import ArepoSlicePlot
from bob.plots.bobSlice import Slice
from bob.plots.slice_1d import Slice1d
from bob.plots.shadowingVolume import ShadowingVolume
from bob.plots.temperatureDensityHistogram import TemperatureDensityHistogram
from bob.plots.temperatureIonizationHistogram import TemperatureIonizationHistogram
from bob.plots.temperatureOverTime import TemperatureOverTime
from bob.plots.meanFieldOverTime import MeanFieldOverTime
from bob.plots.luminosityOverTime import LuminosityOverTime
from bob.plots.sourcePosition import SourcePosition
from bob.plots.stellarMass import StellarMass
from bob.plots.luminosityOverHaloMass import LuminosityOverHaloMass
from bob.plots.characteristicRadii import CharacteristicRadiiOverTime
from bob.plots.meanIonizationRedshift import MeanIonizationRedshift
from bob.plots.sourceField import SourceField
from bob.plots.resolvedEscapeFraction import ResolvedEscapeFraction
from bob.plots.runTime import RunTime
from bob.plots.h2Expansion import H2Expansion
from bob.plots.hExpansion import HExpansion
from bob.plots.expansion import Expansion
from bob.plots.convergence import Convergence
from bob.plots.chainedTimeSeries import ChainedTimeSeries

postprocessingFunctions: List[Type[PostprocessingFunction]] = [
    SliceWithStarParticles,
    Ionization,
    IonizationRate,
    IonizationTime,
    IonizationBinned,
    IonizationLevel,
    MeanFieldOverTime,
    ThomsonScattering,
    ArepoSlicePlot,
    Slice,
    Slice1d,
    ShadowingVolume,
    TemperatureDensityHistogram,
    TemperatureIonizationHistogram,
    TemperatureOverTime,
    LuminosityOverTime,
    SourcePosition,
    StellarMass,
    LuminosityOverHaloMass,
    CharacteristicRadiiOverTime,
    MeanIonizationRedshift,
    SourceField,
    ResolvedEscapeFraction,
    RunTime,
    H2Expansion,
    HExpansion,
    Expansion,
    Convergence,
]

for function in postprocessingFunctions:
    function.name = function.__name__
    function.name = function.name[0].lower() + function.name[1:]


def getFunctionByName(name: str) -> Type[PostprocessingFunction]:
    try:
        return next(function for function in postprocessingFunctions if function.__name__.lower() == name.lower())
    except StopIteration:
        print(f"Plot function not found: {name}. Available functions:")
        for function in postprocessingFunctions:
            print(function.__name__)
        raise
