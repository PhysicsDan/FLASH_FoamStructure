import flash.pyFlash4.Grid as grid
import flash.pyFlash4.Driver as dr
import flash.pyFlash4.RadTrans as rt
import flash.parm as p
from   flash.FlashH import *
from   flash.constantsH import *
from   flash.Simulation_base import pySimulation

import numpy as np

if not 'CHAM_SPEC' in locals():
    CHAM_SPEC = 1
    TARG_SPEC = 2

class Simulation(pySimulation):

    def init(self):
        eV2K = 11604.5221
        self.targetRadius = p.sim_targetRadius.getVal()
        self.targetHeight = p.sim_targetHeight.getVal()
        self.vacuumHeight = p.sim_vacuumHeight.getVal()
        self.rhoTarg      = p.sim_rhoTarg.getVal()
        self.teleTarg     = p.sim_teleTarg.getVal()
        self.tionTarg     = p.sim_tionTarg.getVal()
        self.tradTarg     = p.sim_tradTarg.getVal()
        self.rhoCham      = p.sim_rhoCham.getVal()
        self.teleCham     = p.sim_teleCham.getVal()
        self.tionCham     = p.sim_tionCham.getVal()
        self.tradCham     = p.sim_tradCham.getVal()
        self.smallX       = p.smallx.getVal()
        self.initGeom     = p.sim_initGeom.getVal()
        #RadSlab parms
        self.radSlab        = p.sim_radSlab.getVal()
        self.radSourceType  = p.sim_radSourceType.getVal()
        self.radSourceTmax  = p.sim_radSourceTMax.getVal()*eV2K
        self.radSourceTMin  = p.sim_radSourceTMin.getVal()*eV2K
        self.radSourceStart = p.sim_radSourceStart.getVal()
        self.radSourceStop  = p.sim_radSourceStop.getVal()
        self.radSourcePeak  = p.sim_radSourcePeak.getVal()
        self.radSourceFWHM  = p.sim_radSourceFWHM.getVal()
        self.nG             = p.rt_mgdNumGroups.getVal()
        self.mgdBC = []
        self.mgdBC.append(p.rt_mgdXlBoundaryType.getVal().upper())
        self.mgdBC.append(p.rt_mgdXrBoundaryType.getVal().upper())
        self.mgdBC.append(p.rt_mgdYlBoundaryType.getVal().upper())
        self.mgdBC.append(p.rt_mgdYrBoundaryType.getVal().upper())
        self.mgdBC.append(p.rt_mgdZlBoundaryType.getVal().upper())
        self.mgdBC.append(p.rt_mgdZrBoundaryType.getVal().upper())

        if (self.radSlab and p.useEnergyDeposition.getVal()):
            print ('WARNING: sim_radSlab & useEnergyDeposition both True')

    def isTargSlab(self, x, y):
        if NDIM == 1 :
            if (x <= self.targetHeight + self.vacuumHeight and 
                x >= self.vacuumHeight):
                return TARG_SPEC
        elif NDIM == 2 or NDIM == 3:
            if  (x <= self.targetRadius and 
                 y <= self.targetHeight + self.vacuumHeight and 
                 y >= self.vacuumHeight):
                return TARG_SPEC

        return CHAM_SPEC

    def isTargSphere(self, x, y, z):
        r = np.sqrt(x*x + y*y + z*z)
        if r <= self.targetRadius:
            return TARG_SPEC
        return CHAM_SPEC

    def isTarg(self, x, y, z):
        if self.initGeom == "slab":
            return self.isTargSlab(x,y)
        else:
            return self.isTargSphere(x, y, z)

    def initBlock(self, blockID):
        block = grid.Block(blockID)
        solnVec = np.array(block, copy=False)
        xx = np.array(block.xCoord)
        yy = np.array(block.yCoord)
        zz = np.array(block.zCoord)

        for (i,j,k) in np.ndindex(solnVec.shape[1:]):
            rho  = self.rhoCham
            tele = self.teleCham
            tion = self.tionCham
            trad = self.tradCham

            species = self.isTarg(xx[i], yy[j], zz[k])
            if species == TARG_SPEC:
                rho  = self.rhoTarg
                tele = self.teleTarg
                tion = self.tionTarg
                trad = self.tradTarg

            solnVec[DENS_VAR,i,j,k] = rho
            solnVec[TEMP_VAR,i,j,k] = tele
            if 'FLASH_UHD_3T' in globals():
                solnVec[TION_VAR,i,j,k] = tion
                solnVec[TELE_VAR,i,j,k] = tele

                tradActual = rt.mgdEFromT(blockID, [i,j,k], trad)
                solnVec[TRAD_VAR,i,j,k] = tradActual

            if NSPECIES > 0 :
                for n in range(SPECIES_BEGIN,SPECIES_END):
                    if (n == species):
                        solnVec[n,i,j,k] = 1. - (NSPECIES-1)*self.smallX
                    else:
                        solnVec[n,i,j,k] = self.smallX

            if NFACE_VARS > 0:
                faceX = gr.Block(blockID, FACEX)
                solnX = np.array(faceX, copy=False)
                faceY = gr.Block(blockID, FACEY)
                solnY = np.array(faceY, copy=False)
                for (i,j,k) in np.ndindex(solnX.shape[1:]):
                    solnX[MAG_FACE_VAR,i,j,k] = 0.
                for (i,j,k) in np.ndindex(solnY.shape[1:]):
                    solnY[MAG_FACE_VAR,i,j,k] = 0.
            if NFACE_VARS > 2:
                faceZ = gr.Block(blockID, FACEZ)
                solnZ = np.array(faceZ, copy=False)
                for (i,j,k) in np.ndindex(solnZ.shape[1:]):
                    solnZ[MAG_FACE_VAR,i,j,k] = 0.

    def adjustEvolution(self):
        if not self.radSlab: return

        stime = dr.simTime()
        if (stime < self.radSourceStart or stime >= self.radSourceStop):
            for f in range(2*NDIM):
                # set to reflecting if radiation source is not on
                if self.mgdBC[f] == 'DIRICHLET':
                    [rt.mgdSetBC(ig=n, f=f, bcType=REFLECTING) for n in range(self.nG)]
            return

        # radiation source is on
        tmax = self.radSourceTmax
        trad = tmax
        if self.radSourceType == 1:
            tmin = self.radSourceTmax
            peak = self.radSourcePeak
            fwhm = self.radSourceFWHM
            sigm = fwhm/(2.*np.sqrt(2.*np.log(2.)))
            trad = (tmax-tmin)*np.exp(-(stime-peak)**2/(2.*sigm**2)) + tmin

        urad = rt.mgdUFromT(trad)
        for f in range(2*NDIM):
            if self.mgdBC[f] == 'DIRICHLET':
                [rt.mgdSetBC(ig=n, f=f, bcType=DIRICHLET, bcValue=urad[n]) for n in range(self.nG)]




