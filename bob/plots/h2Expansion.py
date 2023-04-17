import matplotlib.pyplot as plt
import numpy as np
import astropy.units as pq

from bob.simulation import Simulation
from bob.snapshot import Snapshot
from bob.postprocessingFunctions import SnapFn
from bob.result import Result
from bob.plotConfig import PlotConfig
from bob.fieldOverRadius import getDataForRadii
from bob.basicField import BasicField
from bob.temperature import Temperature


class H2Expansion(SnapFn):
    def __init__(self, config: PlotConfig) -> None:
        super().__init__(config)
        self.config.setDefault("num", 20)
        self.config.setDefault("xLabel", "r [UNIT]")
        self.config.setDefault("yLabel", "F [UNIT]")
        self.config.setDefault("xUnit", "pc")
        self.config.setDefault("yUnit", "1 / s")

    def post(self, sim: Simulation, snap: Snapshot) -> Result:
        result = Result()
        boxSize = sim.params["BoxSize"] / 2.0
        lengthUnit = sim.params["UnitLength_in_cm"] * pq.cm
        result.radii = np.linspace(0, boxSize, num=self.config["num"]) * lengthUnit
        coordinates = BasicField("Coordinates").getData(snap)
        center = np.array([1, 1, 1]) * boxSize * lengthUnit
        abundances = BasicField("ChemicalAbundances").getData(snap)
        fluxes = BasicField("PhotonFlux").getData(snap)
        temperature = Temperature().getData(snap)

        result.ab0 = getDataForRadii(abundances[:, 0], center, coordinates, result.radii)
        result.ab1 = getDataForRadii(abundances[:, 1], center, coordinates, result.radii)
        ionizationFront = np.argmax(result.ab1 < 0.25)
        result.ionizationFrontRadius = result.radii[ionizationFront]
        result.temperature = getDataForRadii(temperature, center, coordinates, result.radii)
        result.flux0 = getDataForRadii(fluxes[:, 0], center, coordinates, result.radii, mean=False)
        result.flux1 = getDataForRadii(fluxes[:, 1], center, coordinates, result.radii, mean=False)
        result.flux2 = getDataForRadii(fluxes[:, 2], center, coordinates, result.radii, mean=False)
        return result

    def plot(self, plt: plt.axes, result: Result) -> plt.Figure:
        fig, axes = plt.subplots(2, 3, figsize=(12, 6))
        [[ax00, ax01, ax02], [ax10, ax11, ax12]] = axes
        self.setupLabels()
        ax00.plot(result.radii.to(pq.pc), result.ab0)
        ax01.plot(result.radii.to(pq.pc), result.ab1)
        ax02.plot(result.radii.to(pq.pc), result.temperature.to_value(pq.K))
        ax10.plot(result.radii.to(pq.pc), result.flux1)
        ax11.plot(result.radii.to(pq.pc), result.flux2)
        ax12.plot(result.radii.to(pq.pc), result.flux0)
        fluxes = [result.flux1, result.flux2, result.flux0]
        for iax, ax in enumerate([ax10, ax11, ax12]):
            ax.set_yscale("log")
            max_flux = np.max(fluxes[iax]).to_value(1 / pq.s)
            ax.set_ylim(max_flux / 5e2, max_flux * 1.01)
        for ax in axes[1]:
            ax.set_xlabel("r [pc]")
            ax.axvline(result.ionizationFrontRadius.to_value(pq.pc), c="red", linestyle="-")
        ax00.set_ylabel("H_2")
        ax01.set_ylabel("H+")
        ax02.set_ylabel("T")
        ax10.set_ylabel("F(11.6 eV)")
        ax11.set_ylabel("F(13.6 eV)")
        ax12.set_ylabel("F(5.6 eV)")
        return fig
