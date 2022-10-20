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
from bob.plots.shadowingVolume import ShadowingVolume
from bob.plots.temperatureDensityHistogram import TemperatureDensityHistogram
from bob.plots.temperatureIonizationHistogram import TemperatureIonizationHistogram
from bob.plots.temperatureOverTime import TemperatureOverTime
from bob.plots.meanFieldOverTime import MeanFieldOverTime
from bob.plots.luminosityOverTime import LuminosityOverTime
from bob.plots.sourcePosition import SourcePosition
from bob.plots.stellarMass import StellarMass

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
    ShadowingVolume,
    TemperatureDensityHistogram,
    TemperatureIonizationHistogram,
    TemperatureOverTime,
    LuminosityOverTime,
    SourcePosition,
    StellarMass,
]

for function in postprocessingFunctions:
    function.name = function.__name__
    function.name = function.name[0].lower() + function.name[1:]


def getFunctionByName(name: str) -> Type[PostprocessingFunction]:
    return next(function for function in postprocessingFunctions if function.__name__.lower() == name.lower())
