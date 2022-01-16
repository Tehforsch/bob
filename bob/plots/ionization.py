import re
from typing import List, Tuple, Any
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.ticker

from astropy.cosmology import FlatLambdaCDM, z_at_value
import astropy.units as u

from bob.simulationSet import SimulationSet
from bob.simulation import Simulation
from bob.postprocessingFunctions import addPlot


class IonizationData:
    def __init__(self, sims: List[Simulation]):
        data = []
        for sim in sims:
            assert sim.params.get("ComovingIntegrationOn") == 1
            cosmology = sim.getCosmology()
            # "Time" is just the scale factor here. To make sure that this is true, check that ComovingIntegrationOn is 1
            regex = re.compile("Time ([0-9.+]+): Volume Av. H ionization: ([0-9.+]+), Mass Av. H ionization: ([0-9.+]+)")
            for line in sim.log:
                match = regex.match(line)
                if match is not None:
                    data.append([float(x) for x in match.groups()])

        self.scale_factor = np.array([d[0] for d in data])
        self.volumeAv = np.array([d[1] for d in data])
        self.massAv = np.array([d[2] for d in data])
        self.neutralVolumeAv = 1.0 - self.volumeAv
        self.neutralMassAv = 1.0 - self.massAv
        self.redshift = z_at_value(cosmology.scale_factor, self.scale_factor)


@addPlot(None)
def ionization(ax1: plt.axes, sims: SimulationSet) -> None:
    _, (ax1) = ax1.subplots()
    data = IonizationData([sim for sim in sims])
    # ax1.set_yscale("log")
    # ax1.set_xlim(10, 6.5)
    # ax1.set_xlabel("z")
    # ax1.set_ylabel("$x_{\\mathrm{H}+}$")
    # ax1.plot(data.redshift, data.massAv, label="Mass av.", marker=".")
    # ax1.plot(data.redshift, data.volumeAv, label="Volume av.", marker="o")
    # ax1.plot(data.redshift, 1.0 - data.massAv, label="Mass av.", marker=".")
    # ax1.plot(data.redshift, 1.0 - data.volumeAv, label="Volume av.", marker="o")
    # ax1.legend()
    plt.style.use("classic")
    plot_xhi([data.neutralVolumeAv, data.neutralMassAv], [data.redshift, data.redshift], ["L35N270TNG volume av.", "L35N270TNG mass av."])
    plt.legend(loc="center right")


def plot_xhi(
    sim_xhis_list: List[np.ndarray], sim_zeds_list: List[np.ndarray], sim_label_list: List[str], xhi_min: float = 1e-5, output_path: str = "."
) -> List[plt.axes]:
    """
    This should be OK, but be aware I threw this together without testing the function
    I'm hoping that you can call the function from wherever so that you never have to see this very ugly code
    If you want several simulation curves, you'll want to handle the sim_xhis, sim_zeds, and sim_labels differently. In principle you'd only need to code some kind of loop around the .plot(...) statements in the function
    """
    # FIGURE SETUP
    label_font_size = 17
    tics_label_size = 15
    split_xhi = 1e-1
    n_split = 4

    assert xhi_min < split_xhi, "xhi_min cannot be lower than %f" % split_xhi

    fig_split_xHI = plt.figure(figsize=(10, 10), tight_layout=True)
    gs = gridspec.GridSpec(n_split, 1, hspace=0)

    log_xHI_ax = fig_split_xHI.add_subplot(gs[-1, :])
    lin_xHI_ax = fig_split_xHI.add_subplot(gs[:-1, :])

    # LINEAR PART OF PLOT

    fan06 = np.reshape(
        [
            6.099644128113878,
            0.0004359415240334025,
            5.850533807829182,
            0.00012089973216672045,
            5.649466192170818,
            0.00008641259285077239,
            5.45017793594306,
            0.00006667934792772513,
            5.250889679715303,
            0.00006726593764703922,
            5.032028469750889,
            0.00005511182476220595,
        ],
        (6, 2),
    )
    fanEryUp06 = np.abs(np.asarray([9.975, 3.457, 1.77, 1.238, 1.238, 0.8796]) * 1e-4 - fan06[:, 1])
    fanEryDw06 = np.abs(np.asarray([2.22, 1.48, 0.688, 0.634, 0.548, 0.539]) * 1e-4 - fan06[:, 1])

    lin_xHI_ax.errorbar([0], [0], yerr=[0], label=r"Ly$\alpha$ forest, Fan+06", c="k", fmt="x", capsize=5)

    bosman21_xHI = np.asarray(
        [
            [5, 5.1, 5.2, 5.3, 5.4, 5.5, 6.5, 5.7, 5.8],
            [3.02, 3.336, 3.636, 3.598, 3.498, 4.328, 5.627, 6.544, 7.087],
            [0.058, 0.164, 0.095, 0.145, 3.332, 4.016, 4.630, 5.99, 6.401],
            [0.23, 0.064, 0.131, 0.566, 3.332, 4.016, 4.630, 5.99, 6.401],
            [False, False, False, False, True, True, True, True, True],
        ]
    )  # z, value, lower lim, upper lim, (bool) lower limit?

    lin_xHI_ax.errorbar([0], [0], yerr=[0], c="green", fmt="x", label=r"Ly$\alpha$ forest, Bosman+21", capsize=5)

    lin_xHI_ax.errorbar([0], [0], yerr=[0], c="grey", fmt="x", label=r"Ly$\alpha$ forest, Becker+15", capsize=5)

    mason18 = [0.59, 7]
    masonUp18 = [0.11]
    masonDw18 = [0.15]

    lin_xHI_ax.errorbar(mason18[1] + 0.05, mason18[0], ([masonDw18, masonUp18]), 0, c="brown", fmt="D", capsize=5)

    ono12 = 0.75
    ono12z = 7
    ono12err = 0.15

    lin_xHI_ax.errorbar(ono12z, ono12, yerr=ono12err, color="brown", fmt="D", capsize=5)

    schenker13 = [0.39, 0.65]
    schenker13z = [7, 8]
    schenker13up = [0.09, 0.1]
    schenker13dw = [0.08, 0.1]

    lin_xHI_ax.errorbar(schenker13z, schenker13, yerr=[schenker13dw, schenker13up], color="brown", fmt="D", capsize=5, lolims=[False, True])

    petericci2014 = 0.51
    petericci2014z = 7
    petericci2014err = [[0], [0.1]]

    lin_xHI_ax.errorbar(petericci2014z - 0.05, petericci2014, yerr=petericci2014err, color="brown", fmt="D", lolims=True, capsize=5)

    zhoag19 = 7.6
    zhoag19m = [0.6]
    zhoag19p = [0.6]
    xhihoag19 = 1 - 0.12
    ermxhihoag19 = [0.05]
    erpxhihoag19 = [0.1]
    lin_xHI_ax.errorbar(zhoag19, xhihoag19, xerr=[zhoag19m, zhoag19p], yerr=[ermxhihoag19, erpxhihoag19], color="brown", capsize=5, fmt="D")

    tilvi14 = 0.3
    tilvi14z = 8
    tilvi14err = [[0], [0.1]]

    lin_xHI_ax.errorbar(tilvi14z + 0.05, tilvi14, yerr=tilvi14err, color="brown", fmt="D", label="LAE fraction", lolims=True, capsize=5)

    mortlock11 = 0.1
    mortlock11z = 7.1
    mortlock11err = [[0], [0.1]]

    lin_xHI_ax.errorbar(mortlock11z, mortlock11, mortlock11err, color="darkolivegreen", fmt="s", lolims=True, capsize=5)

    schroeder13 = 0.1
    schroeder13z = 6.2
    schroeder13err = [[0], [0.1]]

    lin_xHI_ax.errorbar(schroeder13z, schroeder13, yerr=schroeder13err, color="darkolivegreen", fmt="s", lolims=True, capsize=5)

    banados18 = 0.33
    banados18z = 7.09
    banados18err = [[0], [0.1]]

    lin_xHI_ax.errorbar(banados18z, banados18, yerr=banados18err, color="darkolivegreen", fmt="s", lolims=True, capsize=5)

    durovcikova19 = [0.25, 0.60]
    durovcikova19z = [7.0851, 7.5413]
    durovcikova19err = [0.05, 0.11]

    lin_xHI_ax.errorbar(durovcikova19z, durovcikova19, yerr=durovcikova19err, color="darkolivegreen", fmt="s", label="QSO damping wings", capsize=5)

    wang21_xhi = 0.7
    wang21_z = 7
    wang21_xhi_dw = 0.23
    wang21_xhi_up = 0.2

    lin_xHI_ax.errorbar([wang21_z - 0.05], [wang21_xhi], yerr=[[wang21_xhi_dw], [wang21_xhi_up]], color="darkolivegreen", fmt="s", capsize=5)

    totani16 = 0.06
    totani16z = 5.91

    log_xHI_ax.errorbar(totani16z, totani16, 0, 0, marker="o", color="darkcyan", capsize=5, linestyle="none")
    lin_xHI_ax.errorbar(0.0, 0.0, 0.0, 0.0, marker="o", color="darkcyan", label="GRB damping wing", capsize=5, linestyle="none")
    totani06 = 0.6
    totani06z = 6.295

    ouchi10 = [0.2, 6.6]
    ouchi10_err = 0.2

    lin_xHI_ax.errorbar(
        ouchi10[1] + 0.05, (ouchi10[0] + ouchi10_err), ouchi10_err * 0.5, 0, color="purple", fmt="P", uplims=True, label=r"Ly$\alpha$ LF", capsize=5
    )

    mcgreer15 = [0.11, 0.10]
    mcgreer15z = [5.9, 5.6]

    lin_xHI_ax.errorbar(
        mcgreer15z, mcgreer15, 0.05, color="goldenrod", fmt="p", linestyle="none", uplims=True, label=r"Dark pixel fraction", capsize=5
    )

    lin_xHI_ax.invert_xaxis()
    # lin_xHI_ax.set_xlim(12.5,1)
    lin_xHI_ax.set_ylim(split_xhi, 1.0)
    lin_xHI_ax.grid("on")
    plt.text(4.2 - 1.2, 2.0 / (n_split + 1), "xHI", rotation=90, ha="center", fontsize=label_font_size)

    # lin_xHI_ax.set_title('Average neutral fraction')

    for (sim_xhis, sim_zeds, sim_label) in zip(sim_xhis_list, sim_zeds_list, sim_label_list):
        lin_xHI_ax.plot(sim_zeds, sim_xhis, label=sim_label, linewidth=3)

    lin_xHI_ax.set_xlim(4.2, 12)

    lin_xHI_ax.tick_params(which="both", direction="in", top="on", right="on", bottom="off", labelbottom="off", labelsize=tics_label_size)

    lin_xHI_ax.tick_params(axis="y", pad=+18)

    # lin_leg = lin_xHI_ax.legend(prop={"size": 17}, framealpha=0.0)
    # mv_legend(lin_leg, lin_xHI_ax, -0.025, -0.3)

    # LOG PART OF PLOT

    log_xHI_ax.errorbar(
        bosman21_xHI[0],
        bosman21_xHI[1] * 1e-5,
        yerr=[bosman21_xHI[2] * 1e-5, bosman21_xHI[3] * 1e-5],
        lolims=bosman21_xHI[-1],
        c="green",
        fmt="x",
        capsize=5,
    )  # ,label=r'Ly$\alpha$ forest, Bosman+21')

    print("Becker 2015 data missing - ask joe")
    # log_xHI_ax.errorbar(
    #     becker_2015_xHI[:, 0] - 0.05,
    #     becker_2015_xHI[:, 1] * 1e-5,
    #     yerr=[(becker_2015_xHI[:, 1] - becker_2015_low) * 1e-5, (becker_2015_high - becker_2015_xHI[:, 1]) * 1e-5],
    #     c="grey",
    #     fmt="x",
    #     capsize=5,
    # )  # ,label=r'Ly$\alpha$ forest, Becker+15')
    log_xHI_ax.errorbar(fan06[:, 0], (fan06[:, 1]), ([fanEryDw06, fanEryUp06]), c="k", fmt="x", capsize=5)  # ,label=r'Ly$\alpha$ forest, Fan+06')

    log_xHI_ax.errorbar(mcgreer15z, mcgreer15, 0.05, color="goldenrod", fmt="p", linestyle="none", uplims=True, capsize=5)

    log_xHI_ax.errorbar(mortlock11z, mortlock11, color="darkolivegreen", fmt="s", capsize=5)
    log_xHI_ax.errorbar(schroeder13z, schroeder13, color="darkolivegreen", fmt="s", capsize=5)

    log_xHI_ax.set_xlabel("z", fontsize=label_font_size)

    for (sim_xhis, sim_zeds, sim_label) in zip(sim_xhis_list, sim_zeds_list, sim_label_list):
        log_xHI_ax.plot(sim_zeds, sim_xhis, linewidth=3)

    log_xHI_ax.set_yscale("log")

    log_xHI_ax.set_ylim(xhi_min, split_xhi)
    log_xHI_ax.set_xlim(4.2, 12)

    log_xHI_ax.grid()

    log_xHI_ax.tick_params(which="major", direction="in", top="off", right="on", bottom="on", labelsize=tics_label_size)
    log_xHI_ax.tick_params(which="minor", direction="in", top="off", right="off", bottom="off", left="off")

    plt.draw()
    ylabs_lin = lin_xHI_ax.get_yticklabels()
    ylabs_lin[0].set_text("")
    lin_xHI_ax.set_yticklabels(ylabs_lin)

    locmaj = matplotlib.ticker.LogLocator(base=10, numticks=int(abs(np.log10(split_xhi) - np.log10(1e-5)) + 1))
    log_xHI_ax.yaxis.set_major_locator(locmaj)

    lin_xHI_ax.spines["bottom"].set_visible(False)
    log_xHI_ax.spines["top"].set_visible(False)

    return [lin_xHI_ax, log_xHI_ax]
