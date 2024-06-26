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
                return df.with_columns((pl.lit(n)).alias("n")).with_columns((pl.lit(final_value)).alias("final_value")).with_columns((pl.col("time") / myr_in_s).alias("time_myr"))

        df = pl.concat([getDf(sim) for sim in sims])
        return df

    def plot(self, plt: plt.axes, df: Result) -> None:
        print(df)
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        self.setupLinePlot()
        labels = self.getLabels()
        sns.lineplot(x=df["time_myr"], y=df["value"], linestyle="-", hue=df["n"])
