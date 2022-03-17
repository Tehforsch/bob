from typing import Union, Tuple, TYPE_CHECKING
from pathlib import Path
import numpy as np
import h5py
import re
import quantities as pq
from bob.basicField import BasicField
from bob.util import memoize
from bob.exceptions import BobException
from bob.constants import kB, protonMass, MSun

if TYPE_CHECKING:
    from bob.simulation import Simulation


class SnapNumber:
    def __init__(self, value: Union[int, Tuple[int, int]]):
        self.value = value


class Snapshot:
    def __init__(self, sim: "Simulation", filename: Path) -> None:
        self.filename = filename
        self.coordinates_ = None
        self.name = self.getName()
        if "subbox" in self.name:
            numbers = self.name.replace("subbox", "").split("_")
            self.number: SnapNumber = SnapNumber((int(numbers[0]), int(numbers[1])))
            self.minExtent, self.maxExtent = sim.subboxCoords()
            self.center = (self.maxExtent + self.minExtent) * 0.5
        else:
            self.number = SnapNumber(int(self.name))
            self.minExtent = np.array([0.0, 0.0, 0.0])
            self.maxExtent = np.array([1.0, 1.0, 1.0]) * sim.params["BoxSize"]
            self.center = (self.maxExtent + self.minExtent) * 0.5
        self.hdf5File: h5py.File = h5py.File(self.filename, "r")
        self.initConversionFactors()

    def getName(self) -> str:
        match = re.match("snap_(.*).hdf5", self.filename.name)
        if match is None:
            raise BobException("Wrong snapshot filename")
        else:
            return match.groups()[0]

    @property  # type: ignore
    @memoize
    def coordinates(self) -> np.ndarray:
        return BasicField("Coordinates").getData(self)

    def __repr__(self) -> str:
        return str(self.filename)

    def initConversionFactors(self) -> None:
        gamma = 5.0 / 3.0
        self.h = self.hdf5File["Header"].attrs["HubbleParam"]
        try:
            redsh = self.hdf5File["Header"].attrs["Redshift"]
        except KeyError:
            redsh = 0.0
            print("WARNING: No cosmological units, I am not sure how much of this library will work")

        self.OmegaLambda = self.hdf5File["Header"].attrs["OmegaLambda"]
        if self.OmegaLambda != 0:
            self.Omega0 = self.hdf5File["Header"].attrs["Omega0"]
            # redsh_str = "z" + str(int(round(10 * redsh)))
        self.lengthUnit = self.hdf5File["Header"].attrs["UnitLength_in_cm"] * pq.cm
        self.massUnit = self.hdf5File["Header"].attrs["UnitMass_in_g"] * pq.g
        self.velocityUnit = self.hdf5File["Header"].attrs["UnitVelocity_in_cm_per_s"] * pq.cm / pq.s
        self.timeUnit = 1 if self.hdf5File["Parameters"].attrs["ComovingIntegrationOn"] else self.lengthUnit / self.velocityUnit 
        self.energyUnit = self.lengthUnit**2 / (self.timeUnit**2) * self.massUnit
        self.volumeUnit = self.lengthUnit**3
        self.time = self.hdf5File["Header"].attrs["Time"] * self.timeUnit
        self.z = redsh
        # prefactors derived from that:
        self.dens_prev = (self.massUnit / self.lengthUnit**3) * ((redsh + 1.0) ** 3 * self.h**2)
        self.dens_to_ndens = 1.0 / (protonMass)
        self.temp_prev = ((gamma - 1.0) * protonMass / kB) * self.velocityUnit**2
        self.mass_prev = self.massUnit / MSun / self.h
        self.len_to_phys = 1.0 / self.h / (1.0 + redsh)
        self.l_Mpc = self.lengthUnit / (1.0e6 * pq.pc)
        self.vel_to_phys = self.velocityUnit / np.sqrt(1.0 + redsh)  # in physical cm/s
        self.vel_phys_kms = self.vel_to_phys * 1.0e-5  # in physical km/s

        if self.OmegaLambda != 0:
            # current age of universe (Myr)
            self.age = self.cosmic_time(1 / (1.0 + redsh), 0)
            # time difference to z=14 (Myr)
            self.t14 = self.cosmic_time(1 / (1.0 + redsh), 1.0 / 15.0)

        self.box_vol = (self.hdf5File["Header"].attrs["BoxSize"] * (self.l_Mpc)) ** 3  # Mpc^3
        self.dm_mass = self.mass_prev * self.hdf5File["Header"].attrs["MassTable"][1]  # in MSun

    def cosmic_time(self, a1: float, a0: float) -> float:
        factor1 = 2.0 / (3.0 * np.sqrt(self.OmegaLambda))
        term1 = np.sqrt(self.OmegaLambda / self.Omega0) * a0**1.5
        term2 = np.sqrt(1 + self.OmegaLambda / self.Omega0 * a0**3)
        factor2 = np.log(term1 + term2)

        t0 = factor1 * factor2

        term1 = np.sqrt(self.OmegaLambda / self.Omega0) * a1**1.5
        term2 = np.sqrt(1 + self.OmegaLambda / self.Omega0 * a1**3)
        factor2 = np.log(term1 + term2)
        t1 = factor1 * factor2

        time_diff = t1 - t0
        time_diff = time_diff / (1.0e7 / (1.0e6 * pq.pc) * self.h)
        time_diff = time_diff / (np.pi * 1.0e7 * 1.0e6)

        return time_diff


# # class for storing halo data
# class fof(object):
#     def __init__(self, snap_num, head_dir=None):
#         conv = conversion_factors(snap_nr=snap_num, head_dir=head_dir)
#         fname = "fof_subhalo_tab_{:03d}.hdf5".format(snap_num)
#         if head_dir:
#             fname = os.path.join(head_dir, fname)
#         f = h5py.File(fname, "r")
#         self.f = f
#         self.id = np.array(f["IDs"]["ID"])
#         self.id_len = f["Group"]["GroupLen"]
#         self.id_len_dm = f["Group"]["GroupLenType"][:, 1]
#         self.id_len_gas = f["Group"]["GroupLenType"][:, 0]
#         self.pos = np.array(f["Group"]["GroupPos"]) * conv.l_unit / conv.kpc
#         self.cm = np.array(f["Group"]["GroupCM"])
#         self.vel = conv.vel_phys_kms * np.array(f["Group"]["GroupVel"])
#         self.id_end = np.cumsum(self.id_len)
#         self.id_begin = self.id_end - self.id_len
#         self.r_200 = f["Group"]["Group_R_Crit200"][:]
#         self.m_tot = conv.mass_prev * f["Group"]["GroupMass"]
#         self.m_gas = conv.mass_prev * f["Group"]["GroupMassType"][:, 0]
#         self.m_dm = conv.mass_prev * f["Group"]["GroupMassType"][:, 1]
#         return

#     def get_ids(self, hnum, min_id=None, max_id=None):
#         ids = self.id[self.id_begin[hnum] : self.id_end[hnum]]
#         if min_id:
#             ids = ids[ids >= min_id]
#         if max_id:
#             ids = ids[ids < max_id]
#         return ids

#     def get_ids_gas(self, hnum):
#         return self.get_ids(hnum, min_id=1000000000)

#     def get_ids_dm(self, hnum):
#         return self.get_ids(hnum, max_id=1000000000)
