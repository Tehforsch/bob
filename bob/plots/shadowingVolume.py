from typing import List

import numpy as np
import matplotlib.pyplot as plt
import astropy.units as pq

from bob.result import Result
from bob.plots.timePlots import TimePlot
from bob.snapshot import Snapshot
from bob.basicField import BasicField
from bob.simulation import Simulation
from bob.plotConfig import PlotConfig
from bob.constants import protonMass


class InfiniteCone:
    def __init__(self, tip: np.ndarray, normal: np.ndarray, radiusPerDistance: float, start: np.ndarray) -> None:
        self.tip = tip
        self.normal = normal
        self.radiusPerDistance = radiusPerDistance
        self.start = np.dot(start, self.normal)

    def contains(self, point: np.ndarray) -> bool:
        dist = point - self.tip
        lengthAlongCentralLine = np.dot(dist, self.normal)
        if lengthAlongCentralLine < self.start:
            return False
        coneRadiusAtPoint = lengthAlongCentralLine * self.radiusPerDistance
        orthogonalDistance = np.linalg.norm((point - self.tip) - lengthAlongCentralLine * self.normal)
        return coneRadiusAtPoint >= orthogonalDistance


class ShadowingVolume(TimePlot):
    def __init__(self, config: PlotConfig) -> None:
        config.setDefault("xUnit", pq.kyr)
        config.setDefault("yUnit", 1.0)
        config.setDefault("xLabel", "$t \; [\mathrm{kyr}]$")
        config.setDefault("yLabel", "$\overline{x_{\mathrm{H}}}$")
        config.setDefault("colors", ["r", "b", "g"])
        config.setDefault("labels", ["$32^3$", "$64^3$", "$128^3$"])
        super().__init__(config)

    def plotToBox(self, x: np.ndarray) -> np.ndarray:
        return x + self.center

    def getQuantity(self, sim: Simulation, snap: Snapshot) -> List[float]:
        lengthUnit = snap.lengthUnit
        self.L = sim.boxSize()
        self.center = self.L * np.array([0.5, 0.5, 0.5])
        self.plotCenter = np.array([0.5, 0.5, 0.5])
        distanceFromCenter = 14.0 / 32.0 * self.L
        radiusBlob = 4.0 / 32.0 * self.L
        self.cone1 = InfiniteCone(
            self.plotToBox(distanceFromCenter * np.array([-1.0, 0.0, 0.0])), np.array([1.0, 0.0, 0.0]), radiusBlob / distanceFromCenter, self.center
        )
        self.cone2 = InfiniteCone(
            self.plotToBox(distanceFromCenter * np.array([0.0, -1.0, 0.0])), np.array([0.0, 1.0, 0.0]), radiusBlob / distanceFromCenter, self.center
        )
        densities = BasicField("Density").getData(snap)
        densityThreshold = 100.0 * pq.cm ** (-3) * protonMass
        densities = densities.to(pq.g / pq.cm**3)
        print(sim, snap, len(np.where(densities < densityThreshold)[0]) / len(np.where(densities > densityThreshold)[0]))
        selection = np.array(
            [
                i
                for (i, coord) in enumerate(snap.coordinates)
                if (self.cone1.contains(coord) and self.cone2.contains(coord) and densities[i] < densityThreshold)
            ]
        )
        data = snap.ionized_hydrogen_fraction()[selection]
        masses = BasicField("Masses").getData(snap)[selection]
        return np.sum(data * masses) / np.sum(masses)

    def plot(self, plt: plt.axes, result: Result) -> None:
        self.config["colors"] = ["r", "b", "g"]
        super().plot(plt, result)
        data = oldSweepData()
        labels = ["$32^3$", "$64^3$", "$128^3$"]
        colors = ["r", "b", "g"]
        for (d, label, color) in zip(data, labels, colors):
            plt.plot([x[0] for x in d], [x[1] for x in d], color=color, linestyle="--")
        plt.plot([], [], color="black", linestyle="-", label="Subsweep")
        plt.plot([], [], color="black", linestyle="--", label="Arepo Sweep")
        plt.xlim(0, 50)
        plt.ylim(0, 0.5)
        plt.legend(loc="upper left")

def oldSweepData():
    x32 = [[00.7992867188629553, 0.0038528389894656456], [01.9800561686988747, 0.0038528389894656456], [03.160825618534794, 0.0038528389894656456], [04.341595068370713, 0.0038528389894656456], [05.522364518206631, 0.0038528389894656456], [06.703133968042552, 0.0038528389894656456], [07.88390341787847, 0.0038528389894656456], [09.06467286771439, 0.0038528389894656456], [10.245442317550308, 0.0038528389894656456], [11.426211767386226, 0.0038528389894656456], [12.606981217222147, 0.0038528389894656456], [13.787750667058065, 0.0038528389894656456], [14.968520116893986, 0.0038528389894656456], [16.149289566729905, 0.0038528389894656456], [17.330059016565826, 0.004172957984882597], [18.51082846640174, 0.0047064896439108495], [19.69159791623766, 0.005275590080207726], [20.555114988104677, 0.01664932362122773], [21.50674068199841, 0.02393340270551514], [22.41078509119746, 0.03537981269510926], [23.18023492711651, 0.04473914845966287], [24.59869173373758, 0.0722668414385721], [25.810130519932876, 0.09521124340373388], [26.829885953882076, 0.12797897946238468], [26.9310071371927, 0.12903225806451601], [28.12396156304569, 0.16948477847000898], [29.214908802537664, 0.2081165452653485], [29.24509619218282, 0.20926252771533638], [30.31852296476093, 0.2532136801601734], [31.33827839871013, 0.29518246608524346], [31.356066613798568, 0.29656607700312176], [32.35803383265934, 0.3379370255814711], [33.402061855670105, 0.3798126951092612], [33.43146060523745, 0.38092633900767114], [34.40126883425852, 0.4193548387096774], [34.50488737781556, 0.424844886740012], [35.495638382236315, 0.4630593132154006], [35.518679329694876, 0.46462263598533937], [36.68517049960349, 0.49947970863683666], [36.81871842092836, 0.5076608564802837], [37.7319587628866, 0.5421436004162331], [37.993524388694404, 0.5470147444631609], [38.82632831086439, 0.5702393340270552], [39.281636515788136, 0.5866294701460073], [39.730372720063436, 0.5983350676378771], [40.61149301737102, 0.6237336329666487], [40.824742268041234, 0.6285119667013528], [41.6812053925456, 0.6555671175858482], [42.01887478586231, 0.6614572853247174], [43.19964423569823, 0.6832698379846551], [44.45708702643258, 0.7091207171780469], [45.75797804367606, 0.7292424826042547], [47.14065395787785, 0.7512087431945316], [48.444100753151275, 0.7683122438068081], [49.87278067189213, 0.7893003630221997], [51.23501036185436, 0.807046642252258], [52.77103295785302, 0.8252959656179714], [54.1307068697853, 0.8401637145162248], [55.77662792107172, 0.8558139765143864], [57.04684960195583, 0.8665735316381226], [58.4208358708558, 0.8764331966969643], [59.676745194772195, 0.8841800763860543]]
    x64 = [[0.3330689928628061, 0.0011217481789800328], [13.941316415543218, 0.0015123817118188811], [19.460745440126885, 0.0030405827263266776], [21.554321966693102, 0.0010405827263266776], [23.838223632038066, 0.010405827263267442], [25.884218873909596, 0.02393340270551514], [27.882632831086433, 0.047866805411030056], [29.643140364789843, 0.07596253902185224], [31.498810467882628, 0.10613943808532766], [33.21173671689135, 0.13735691987513], [36.304520222045994, 0.2081165452653485], [39.587628865979376, 0.27679500520291356], [44.01268834258524, 0.38189386056191477], [48.723235527359236, 0.48074921956295524], [52.196669310071364, 0.5483870967741936], [55.71768437747818, 0.6045785639958376], [59.42902458366376, 0.6566077003121749]]
    x128 = [[0.3806502775574927, 0.0031217481789800328], [19.603489294210945, 0.0015608740894905715], [25.265662172878663, 0.004162330905306932], [28.83425852498017, 0.008324661810613865], [32.26011102299761, 0.02809573361082185], [36.68517049960349, 0.07492195629552545], [40.72957969865186, 0.13215400624349638], [45.67803330689928, 0.20707596253902183], [48.96114195083267, 0.25910509885535904], [52.291831879460744, 0.3121748178980229], [55.43219666931007, 0.3590010405827264], [59.76209357652657, 0.4172736732570239]]
    return x32, x64, x128
