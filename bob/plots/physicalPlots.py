from typing import List
import numpy as np

import matplotlib.pyplot as plt
from bob.field import Field
from bob.snapshot import Snapshot
from bob.basicField import BasicField
from bob.simulation import Simulation
from bob.temperature import Temperature
from bob.plots.slicePlot import VoronoiSlice
from bob.postprocessingFunctions import addToList

import bob.plots.ionizationTime
import bob.plots.temperaturePlots

# import bob.plots.thomsonScattering
# import bob.plots.image

addToList("slice", VoronoiSlice())
