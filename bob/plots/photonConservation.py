import matplotlib.pyplot as plt
import astropy.units as pq
from bob.postprocessingFunctions import MultiSetFn
from bob.result import Result
from bob.multiSet import MultiSet
from bob.plots.timePlots import addTimeArg
from bob.util import getArrayQuantity

from bob.plotConfig import PlotConfig
import polars as pl
import seaborn as sns


class PhotonConservation(MultiSetFn):
    def __init__(self, config: PlotConfig) -> None:
        config.setDefault("quotient", None)
        super().__init__(config)
        config.setDefault("xUnit", "1.0", override=True)
        config.setDefault("yUnit", "1.0", override=True)
        config.setDefault("xLabel", "t [Myr]")
        config.setDefault("yLabel", "y")

    def post(self, sims: MultiSet) -> Result:
        if len(sims) > 1:
            raise NotImplementedError("To do this, properly label sims in the df i guess")
        sims = next(iter(sims))

        def getDf(sim):
            with sim.comovingUnits() as _:
                df = sim.get_timeseries_as_dataframe("lost_photons_fraction", 1.0)
                n = sim.params["sweep"]["num_timestep_levels"]
                final_value = df.top_k(1, by="time")["value"]
                myr_in_s = (1.0 * pq.Myr).to_value(pq.s)
                resolution = int(sim.params["input"]["paths"][0].replace("ics/", "").replace(".hdf5", ""))
                dt = pq.Quantity(sim.params["sweep"]["max_timestep"]).to_value(pq.s) / myr_in_s
                df = pl.DataFrame({
                    "n": n,
                    "dt": dt,
                    "resolution": resolution,
                    "final_value": final_value
                    })
                print(df)
                return df

        df = pl.concat([getDf(sim) for sim in sims])
        return df

    def plot(self, plt: plt.axes, df: Result) -> None:
        df = df
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        self.setupLinePlot()
        labels = self.getLabels()
        sns.lineplot(x=df["resolution"], y=df["final_value"], linestyle="-", hue=df["dt"])
