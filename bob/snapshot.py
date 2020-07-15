from pathlib import Path
import numpy as np
import h5py
import re
from bob.basicField import BasicField
from bob.util import memoize
from bob.exceptions import BobException


class Snapshot:
    def __init__(self, filename: Path) -> None:
        self.filename = filename
        self.coordinates_ = None
        self.name = self.getName()
        self.hdf5File = h5py.File(self.filename, "r")
        self.initConversionFactors()

    def getName(self) -> str:
        match = re.match("snap_(.*).hdf5", self.filename.name)
        if match is None:
            raise BobException("Wrong snapshot filename")
        else:
            return match.groups()[0]

    @property  # type: ignore
    @memoize
    def coordinates(self) -> None:
        return BasicField("Coordinates").getData(self)

    def __repr__(self) -> str:
        return str(self.filename)

    def initConversionFactors(self):
        mu = 1.22
        mp = 1.672623e-24
        self.mp = mp
        kb = 1.380658e-16
        gamma = 5.0 / 3.0
        pc = 3.0857e18
        self.pc = pc
        self.kpc = pc * 1000
        self.M_sun = 1.98855e33  # g
        self.kb = kb
        self.mp = mp

        h = self.hdf5File["Header"].attrs["HubbleParam"]
        self.h = self.hdf5File["Header"].attrs["HubbleParam"]
        try:
            redsh = self.hdf5File["Header"].attrs["Redshift"]
        except:
            redsh = 0.0
            print("WARNING: No cosmological units, I am not sure " + "how much of this library will work")

        l_unit = self.hdf5File["Header"].attrs["UnitLength_in_cm"]
        m_unit = self.hdf5File["Header"].attrs["UnitMass_in_g"]
        v_unit = self.hdf5File["Header"].attrs["UnitVelocity_in_cm_per_s"]
        self.OmegaLambda = self.hdf5File["Header"].attrs["OmegaLambda"]
        self.Omega0 = self.hdf5File["Header"].attrs["Omega0"]
        redsh_str = "z" + str(int(round(10 * redsh)))
        self.l_unit = self.hdf5File["Header"].attrs["UnitLength_in_cm"]
        self.m_unit = self.hdf5File["Header"].attrs["UnitMass_in_g"]
        self.v_unit = self.hdf5File["Header"].attrs["UnitVelocity_in_cm_per_s"]
        self.time = self.hdf5File["Header"].attrs["Time"]
        self.t_unit = l_unit / v_unit
        self.z = redsh
        # prefactors derived from that:
        self.dens_prev = (m_unit / l_unit ** 3) * ((redsh + 1.0) ** 3 * h ** 2)
        self.dens_to_ndens = 1.0 / (mp * mu)
        self.temp_prev = ((gamma - 1.0) * mu * mp / kb) * v_unit ** 2
        self.mass_prev = m_unit / self.M_sun / h
        self.len_to_phys = 1.0 / h / (1.0 + redsh)
        self.l_Mpc = l_unit / (1.0e6 * pc)
        self.vel_to_phys = v_unit / np.sqrt(1.0 + redsh)  # in physical cm/s
        self.vel_phys_kms = self.vel_to_phys * 1.0e-5  # in physical km/s

        # current age of universe (Myr)
        self.age = self.cosmic_time(1 / (1.0 + redsh), 0)
        # time difference to z=14 (Myr)
        self.t14 = self.cosmic_time(1 / (1.0 + redsh), 1.0 / 15.0)

        self.box_vol = (self.hdf5File["Header"].attrs["BoxSize"] * (self.l_Mpc)) ** 3  # Mpc^3
        self.dm_mass = self.mass_prev * self.hdf5File["Header"].attrs["MassTable"][1]  # in M_sun

    def cosmic_time(All, a1, a0):
        factor1 = 2.0 / (3.0 * np.sqrt(All.OmegaLambda))
        term1 = np.sqrt(All.OmegaLambda / All.Omega0) * a0 ** 1.5
        term2 = np.sqrt(1 + All.OmegaLambda / All.Omega0 * a0 ** 3)
        factor2 = np.log(term1 + term2)

        t0 = factor1 * factor2

        term1 = np.sqrt(All.OmegaLambda / All.Omega0) * a1 ** 1.5
        term2 = np.sqrt(1 + All.OmegaLambda / All.Omega0 * a1 ** 3)
        factor2 = np.log(term1 + term2)
        t1 = factor1 * factor2

        time_diff = t1 - t0
        time_diff = time_diff / (1.0e7 / (1.0e6 * All.pc) * All.h)
        time_diff = time_diff / (np.pi * 1.0e7 * 1.0e6)

        return time_diff


# class for storing halo data
class fof(object):
    def __init__(self, snap_num, head_dir=None):
        conv = conversion_factors(snap_nr=snap_num, head_dir=head_dir)
        fname = "fof_subhalo_tab_{:03d}.hdf5".format(snap_num)
        if head_dir:
            fname = os.path.join(head_dir, fname)
        f = h5py.File(fname, "r")
        self.f = f
        self.id = np.array(f["IDs"]["ID"])
        self.id_len = f["Group"]["GroupLen"]
        self.id_len_dm = f["Group"]["GroupLenType"][:, 1]
        self.id_len_gas = f["Group"]["GroupLenType"][:, 0]
        self.pos = np.array(f["Group"]["GroupPos"]) * conv.l_unit / conv.kpc
        self.cm = np.array(f["Group"]["GroupCM"])
        self.vel = conv.vel_phys_kms * np.array(f["Group"]["GroupVel"])
        self.id_end = np.cumsum(self.id_len)
        self.id_begin = self.id_end - self.id_len
        self.r_200 = f["Group"]["Group_R_Crit200"][:]
        self.m_tot = conv.mass_prev * f["Group"]["GroupMass"]
        self.m_gas = conv.mass_prev * f["Group"]["GroupMassType"][:, 0]
        self.m_dm = conv.mass_prev * f["Group"]["GroupMassType"][:, 1]
        return

    def get_ids(self, hnum, min_id=None, max_id=None):
        ids = self.id[self.id_begin[hnum] : self.id_end[hnum]]
        if min_id:
            ids = ids[ids >= min_id]
        if max_id:
            ids = ids[ids < max_id]
        return ids

    def get_ids_gas(self, hnum):
        return self.get_ids(hnum, min_id=1000000000)

    def get_ids_dm(self, hnum):
        return self.get_ids(hnum, max_id=1000000000)
