from typing import List
import numpy as np

import matplotlib.pyplot as plt
from bob.snapshot import Snapshot
from bob.simulation import Simulation
from bob.plots.slicePlot import VoronoiSlice
from bob.postprocessingFunctions import addToList

import bob.plots.ionizationTime
import bob.plots.timePlots
import bob.plots.thomsonScattering
# import bob.plots.image

addToList("slice", VoronoiSlice())
