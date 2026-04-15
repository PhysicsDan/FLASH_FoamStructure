import os

import flash.parm as p
import flash.pyFlash4.Driver as dr
import flash.pyFlash4.Grid as grid
import flash.pyFlash4.RadTrans as rt
import numpy as np
from flash.constantsH import *
from flash.FlashH import *
from flash.Simulation_base import pySimulation

# TODO ADD IN A FREEZE TO STOP THE TARGET PRE-EXPANDING UNPHYSICALLY

# Species index convention:
#   CHAM_SPEC = 1 (always the first species = chamber/background)
#   Layer species = 2, 3, 4, ... (in order of LAYERS list)
if not "CHAM_SPEC" in locals():
    CHAM_SPEC = 1


class Simulation(pySimulation):
    def init(self):
        eV2K = 11604.5221

        # ----- Geometry parameters -----
        self.targetRadius = p.sim_targetRadius.getVal()
        self.vacuumHeight = p.sim_vacuumHeight.getVal()
        self.smallX = p.smallx.getVal()
        self.initGeom = p.sim_initGeom.getVal()

        # ----- Load layer definitions -----
        self.numLayers = p.sim_numLayers.getVal()
        self.layers = []
        for n in range(1, self.numLayers + 1):
            layer = {
                "rho": getattr(p, f"sim_rho_{n}").getVal(),
                "tele": getattr(p, f"sim_tele_{n}").getVal(),
                "tion": getattr(p, f"sim_tion_{n}").getVal(),
                "trad": getattr(p, f"sim_trad_{n}").getVal(),
                "height": getattr(p, f"sim_height_{n}").getVal(),
                "radius": getattr(p, f"sim_radius_{n}").getVal(),
                "spec": CHAM_SPEC + n,  # species index: 2, 3, 4, ...
            }
            self.layers.append(layer)

        # Compute cumulative y-boundaries for sequential stacking
        # Layer 0: vacuumHeight -> vacuumHeight + height[0]
        # Layer 1: vacuumHeight + height[0] -> vacuumHeight + height[0] + height[1]
        # etc.
        y_start = self.vacuumHeight
        for layer in self.layers:
            layer["ymin"] = y_start
            layer["ymax"] = y_start + layer["height"]
            y_start = layer["ymax"]

        # ----- Chamber (background) parameters -----
        self.rhoCham = p.sim_rhoCham.getVal()
        self.teleCham = p.sim_teleCham.getVal()
        self.tionCham = p.sim_tionCham.getVal()
        self.tradCham = p.sim_tradCham.getVal()

        # ----- Custom density map -----
        self.customDensMap = p.sim_customDensMap.getVal()
        if self.customDensMap:
            densMapFile = p.sim_densMapFile.getVal().strip()
            print(f"[Simulation] Loading custom density map from: {densMapFile}")
            data = np.load(densMapFile)
            self.densMap_x = data["x"]  # 1D array of x coords
            self.densMap_y = data["y"]  # 1D array of y coords
            self.densMap_density = data["density"]  # 2D array (Nx, Ny)
            self.densMap_species = data["species"]  # 2D array (Nx, Ny), int

            # Optional: load temperature arrays if present
            self.densMap_tele = data["tele"] if "tele" in data else None
            self.densMap_tion = data["tion"] if "tion" in data else None
            self.densMap_trad = data["trad"] if "trad" in data else None

        # ----- RadSlab parameters -----
        self.radSlab = p.sim_radSlab.getVal()
        self.radSourceType = p.sim_radSourceType.getVal()
        self.radSourceTmax = p.sim_radSourceTMax.getVal() * eV2K
        self.radSourceTMin = p.sim_radSourceTMin.getVal() * eV2K
        self.radSourceStart = p.sim_radSourceStart.getVal()
        self.radSourceStop = p.sim_radSourceStop.getVal()
        self.radSourcePeak = p.sim_radSourcePeak.getVal()
        self.radSourceFWHM = p.sim_radSourceFWHM.getVal()
        self.nG = p.rt_mgdNumGroups.getVal()
        self.mgdBC = []
        self.mgdBC.append(p.rt_mgdXlBoundaryType.getVal().upper())
        self.mgdBC.append(p.rt_mgdXrBoundaryType.getVal().upper())
        self.mgdBC.append(p.rt_mgdYlBoundaryType.getVal().upper())
        self.mgdBC.append(p.rt_mgdYrBoundaryType.getVal().upper())
        self.mgdBC.append(p.rt_mgdZlBoundaryType.getVal().upper())
        self.mgdBC.append(p.rt_mgdZrBoundaryType.getVal().upper())

        if self.radSlab and p.useEnergyDeposition.getVal():
            print("WARNING: sim_radSlab & useEnergyDeposition both True")

    # ------------------------------------------------------------------
    #  Geometry helpers: determine which species a coordinate belongs to
    # ------------------------------------------------------------------

    def isTargSlab(self, x, y):
        """Check layers from last (outermost) to first (innermost).
        For sequential stacking each layer occupies:
          ymin <= y < ymax  AND  x <= radius
        Returns the species index, or CHAM_SPEC for the background.
        """
        if NDIM == 1:
            for layer in reversed(self.layers):
                if layer["ymin"] <= x < layer["ymax"]:
                    return layer["spec"]
        elif NDIM == 2 or NDIM == 3:
            for layer in reversed(self.layers):
                if x <= layer["radius"] and layer["ymin"] <= y < layer["ymax"]:
                    return layer["spec"]

        return CHAM_SPEC

    def isTargSphere(self, x, y, z):
        """Sphere geometry: only uses first layer's radius."""
        r = np.sqrt(x * x + y * y + z * z)
        if self.numLayers > 0 and r <= self.layers[0]["radius"]:
            return self.layers[0]["spec"]
        return CHAM_SPEC

    def isTarg(self, x, y, z):
        if self.initGeom == "slab":
            return self.isTargSlab(x, y)
        else:
            return self.isTargSphere(x, y, z)

    # ------------------------------------------------------------------
    #  Custom density map lookup
    # ------------------------------------------------------------------

    def _lookup_densmap(self, x, y):
        """Look up density and species from the loaded .npz arrays
        using nearest-neighbour interpolation on the 1D coord arrays.
        Returns (rho, species_index, tele, tion, trad).
        """
        ix = np.searchsorted(self.densMap_x, x, side="right") - 1
        iy = np.searchsorted(self.densMap_y, y, side="right") - 1

        # Clamp to valid range
        ix = max(0, min(ix, len(self.densMap_x) - 1))
        iy = max(0, min(iy, len(self.densMap_y) - 1))

        rho = self.densMap_density[ix, iy]
        spec_id = int(self.densMap_species[ix, iy])

        # Map species_id -> material properties for temperature
        # spec_id: 0 = cham, 1 = layer 1, 2 = layer 2, ...
        if spec_id == 0:
            tele = self.teleCham
            tion = self.tionCham
            trad = self.tradCham
        elif 1 <= spec_id <= self.numLayers:
            layer = self.layers[spec_id - 1]
            tele = layer["tele"]
            tion = layer["tion"]
            trad = layer["trad"]
        else:
            # Fallback to chamber
            tele = self.teleCham
            tion = self.tionCham
            trad = self.tradCham

        # Override with per-cell temperatures from map if available
        if self.densMap_tele is not None:
            tele = self.densMap_tele[ix, iy]
        if self.densMap_tion is not None:
            tion = self.densMap_tion[ix, iy]
        if self.densMap_trad is not None:
            trad = self.densMap_trad[ix, iy]

        # Convert spec_id (0-based) to FLASH species index (1-based)
        # 0 -> CHAM_SPEC (1), 1 -> CHAM_SPEC+1 (2), etc.
        species = CHAM_SPEC + spec_id

        return rho, species, tele, tion, trad

    # ------------------------------------------------------------------
    #  Block initialisation
    # ------------------------------------------------------------------

    def initBlock(self, blockID):
        block = grid.Block(blockID)
        solnVec = np.array(block, copy=False)
        xx = np.array(block.xCoord)
        yy = np.array(block.yCoord)
        zz = np.array(block.zCoord)

        for i, j, k in np.ndindex(solnVec.shape[1:]):
            # TODO: Check can this be sped up with a np.where or something like that?
            if self.customDensMap:
                # --- Custom density map path ---
                rho, species, tele, tion, trad = self._lookup_densmap(xx[i], yy[j])
            else:
                # --- Geometric layer path ---
                # Default to chamber values
                rho = self.rhoCham
                tele = self.teleCham
                tion = self.tionCham
                trad = self.tradCham
                species = CHAM_SPEC

                spec_id = self.isTarg(xx[i], yy[j], zz[k])
                if spec_id != CHAM_SPEC:
                    # Find the matching layer (spec_id = CHAM_SPEC + layer_index + 1)
                    layer_idx = spec_id - CHAM_SPEC - 1
                    if 0 <= layer_idx < self.numLayers:
                        layer = self.layers[layer_idx]
                        rho = layer["rho"]
                        tele = layer["tele"]
                        tion = layer["tion"]
                        trad = layer["trad"]
                    species = spec_id

            solnVec[DENS_VAR, i, j, k] = rho
            solnVec[TEMP_VAR, i, j, k] = tele
            if "FLASH_UHD_3T" in globals():
                solnVec[TION_VAR, i, j, k] = tion
                solnVec[TELE_VAR, i, j, k] = tele

                tradActual = rt.mgdEFromT(blockID, [i, j, k], trad)
                solnVec[TRAD_VAR, i, j, k] = tradActual

            if NSPECIES > 0:
                for n in range(SPECIES_BEGIN, SPECIES_END):
                    if n == species:
                        solnVec[n, i, j, k] = 1.0 - (NSPECIES - 1) * self.smallX
                    else:
                        solnVec[n, i, j, k] = self.smallX

            if NFACE_VARS > 0:
                faceX = gr.Block(blockID, FACEX)
                solnX = np.array(faceX, copy=False)
                faceY = gr.Block(blockID, FACEY)
                solnY = np.array(faceY, copy=False)
                for i, j, k in np.ndindex(solnX.shape[1:]):
                    solnX[MAG_FACE_VAR, i, j, k] = 0.0
                for i, j, k in np.ndindex(solnY.shape[1:]):
                    solnY[MAG_FACE_VAR, i, j, k] = 0.0
            if NFACE_VARS > 2:
                faceZ = gr.Block(blockID, FACEZ)
                solnZ = np.array(faceZ, copy=False)
                for i, j, k in np.ndindex(solnZ.shape[1:]):
                    solnZ[MAG_FACE_VAR, i, j, k] = 0.0

    def adjustEvolution(self):

        # For RADSLAB only
        if self.radSlab:
            stime = dr.simTime()
            if stime < self.radSourceStart or stime >= self.radSourceStop:
                for f in range(2 * NDIM):
                    # set to reflecting if radiation source is not on
                    if self.mgdBC[f] == "DIRICHLET":
                        [
                            rt.mgdSetBC(ig=n, f=f, bcType=REFLECTING)
                            for n in range(self.nG)
                        ]
                return

            # radiation source is on
            tmax = self.radSourceTmax
            trad = tmax
            if self.radSourceType == 1:
                tmin = self.radSourceTmax
                peak = self.radSourcePeak
                fwhm = self.radSourceFWHM
                sigm = fwhm / (2.0 * np.sqrt(2.0 * np.log(2.0)))
                trad = (tmax - tmin) * np.exp(
                    -((stime - peak) ** 2) / (2.0 * sigm**2)
                ) + tmin

            urad = rt.mgdUFromT(trad)
            for f in range(2 * NDIM):
                if self.mgdBC[f] == "DIRICHLET":
                    [
                        rt.mgdSetBC(ig=n, f=f, bcType=DIRICHLET, bcValue=urad[n])
                        for n in range(self.nG)
                    ]
        else:
            return
