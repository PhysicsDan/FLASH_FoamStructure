def setupArgs():
    args = [
            '-auto',
            '-2d',
            '+cylindrical',
            '-nxb=16',
            '-nyb=16',
            '+hdf5typeio',
            'species=cham,targ',
            '+mtmmmt',
            '+laser',
            '+uhd3t',
            '+mgd',
            'mgd_meshgroups=6',
            '+python'
            ]
    return args


def parms():
    import flash.parm as p
    p.run_comment("Laser Slab Example Simulation") 
    p.log_file("lasslab.log") 
    p.basenm("lasslab_") 

# This particular parfile is used as an example that is described in
# detail in the users guide.

##########################
#                        #
#     I/O PARAMETERS     #
#                        #
##########################

### Checkpoint Options  ###
    p.checkpointFileIntervalTime(1.0) 
    p.checkpointFileIntervalStep(1000) 

### Plot Options ###
    p.plotFileNumber(0) 
    p.plotFileIntervalStep(100) 
    p.plotFileIntervalTime(0.01e-09) 
    p.plot_var_1("dens") 
    p.plot_var_2("depo") 
    p.plot_var_3("tele") 
    p.plot_var_4("tion") 
    p.plot_var_5("trad") 
    p.plot_var_6("ye  ") 
    p.plot_var_7("sumy") 
    p.plot_var_8("cham") 
    p.plot_var_9("targ") 

### Restart Options ###
    p.restart(False) 
    p.checkpointFileNumber(0) 

########################################
#                                      #
#     RADIATION/OPACITY PARAMETERS     #
#                                      #
########################################
    p.rt_useMGD(True) 
    p.rt_mgdNumGroups(6) 
    p.rt_mgdBounds_1(1.0e-01) 
    p.rt_mgdBounds_2(1.0e+00) 
    p.rt_mgdBounds_3(1.0e+01) 
    p.rt_mgdBounds_4(1.0e+02) 
    p.rt_mgdBounds_5(1.0e+03) 
    p.rt_mgdBounds_6(1.0e+04) 
    p.rt_mgdBounds_7(1.0e+05) 
    p.rt_mgdFlMode("fl_harmonic") 
    p.rt_mgdFlCoef(1.0) 

    p.rt_mgdXlBoundaryType("reflecting") 
    p.rt_mgdXrBoundaryType("vacuum") 
    p.rt_mgdYlBoundaryType("vacuum") 
    p.rt_mgdYrBoundaryType("reflecting") 
    p.rt_mgdZlBoundaryType("reflecting") 
    p.rt_mgdZrBoundaryType("reflecting") 

    p.useOpacity(True) 

### SET CHAMBER (HELIUM) OPACITY OPTIONS ###
    p.op_chamAbsorb("op_tabpa") 
    p.op_chamEmiss("op_tabpe") 
    p.op_chamTrans("op_tabro") 
    p.op_chamFileType("ionmix4") 
    p.op_chamFileName("he-imx-005.cn4") 

### SET TARGET (ALUMINUM) OPACITY OPTIONS ###
    p.op_targAbsorb("op_tabpa") 
    p.op_targEmiss("op_tabpe") 
    p.op_targTrans("op_tabro") 
    p.op_targFileType("ionmix4") 
    p.op_targFileName("al-imx-003.cn4") 


############################
#                          #
#     LASER PARAMETERS     #
#                          #
############################
    p.useEnergyDeposition(True) 
    p.ed_maxRayCount(10000) 
    p.ed_gradOrder(2) 

# Activate 3D-in-2D ray trace:
    p.ed_laser3Din2D(True) 
    p.ed_laser3Din2DwedgeAngle(0.1) 


### LASER IO OPTIONS ###
    p.ed_useLaserIO(True) 
    p.ed_laserIOMaxNumberOfPositions(10000) 
    p.ed_laserIOMaxNumberOfRays(128) 

### SETUP LASER PULSES ###
    p.ed_numberOfPulses(1) 

# Define Pulse 1:
    p.ed_numberOfSections_1(4) 
    p.ed_time_1_1(0.0) 
    p.ed_time_1_2(0.1e-09) 
    p.ed_time_1_3(1.0e-09) 
    p.ed_time_1_4(1.1e-09) 

    p.ed_power_1_1(0.0) 
    p.ed_power_1_2(1.0e+09) 
    p.ed_power_1_3(1.0e+09) 
    p.ed_power_1_4(0.0) 

### SETUP LASER BEAM ###
    p.ed_numberOfBeams(1) 

# Setup Gaussian Beam:
    p.ed_lensX_1(1000.0e-04) 
    p.ed_lensY_1(0.0e-04) 
    p.ed_lensZ_1(-1000.0e-04) 
    p.ed_lensSemiAxisMajor_1(10.0e-04) 
    p.ed_targetX_1(0.0e-04) 
    p.ed_targetY_1(0.0e-04) 
    p.ed_targetZ_1(60.0e-04) 
    p.ed_targetSemiAxisMajor_1(10.0e-04) 
    p.ed_targetSemiAxisMinor_1(10.0e-04) 
    p.ed_pulseNumber_1(1) 
    p.ed_wavelength_1(1.053) 
    p.ed_crossSectionFunctionType_1("gaussian2D") 
    p.ed_gaussianExponent_1(4.0) 
    p.ed_gaussianRadiusMajor_1(7.5e-04) 
    p.ed_gaussianRadiusMinor_1(7.5e-04) 
    p.ed_numberOfRays_1(4096) 
    p.ed_gridType_1("radial2D") 
    p.ed_gridnRadialTics_1(64) 
    p.ed_semiAxisMajorTorsionAngle_1(0.0) 
    p.ed_semiAxisMajorTorsionAxis_1("x") 


#################################
#                               #
#     CONDUCTION PARAMETERS     #
#                               #
#################################
    p.useDiffuse(True) 
    p.useConductivity(True) 
    p.diff_useEleCond(True) 
    p.diff_eleFlMode("fl_larsen") 
    p.diff_eleFlCoef(0.06) 
    p.diff_thetaImplct(1.0) 

    p.diff_eleXlBoundaryType("neumann") 
    p.diff_eleXrBoundaryType("neumann") 
    p.diff_eleYlBoundaryType("neumann") 
    p.diff_eleYrBoundaryType("neumann") 
    p.diff_eleZlBoundaryType("neumann") 
    p.diff_eleZrBoundaryType("neumann") 


####################################
#                                  #
#     HEAT EXCHANGE PARAMETERS     #
#                                  #
####################################
    p.useHeatexchange(True) 


##########################
#                        #
#     EOS PARAMETERS     #
#                        #
##########################
    p.eosModeInit("dens_temp_gather") 
    p.smallt(1.0) 
    p.smallx(1.0e-99) 
    p.eos_useLogTables(False) 


############################
#                          #
#     HYDRO PARAMETERS     #
#                          #
############################
    p.useHydro(True) 
     
    p.order(3) # Interpolation order (first/second/third/fifth order)
    p.slopeLimiter("minmod") # Slope limiters (minmod, mc, vanLeer, hybrid, limited)
    p.LimitedSlopeBeta(1.) # Slope parameter for the "limited" slope by Toro
    p.charLimiting(True) # Characteristic limiting vs. Primitive limiting
    p.use_avisc(True) # use artificial viscosity (originally for PPM)
    p.cvisc(0.1) # coefficient for artificial viscosity
    p.use_flattening(False) # use flattening (dissipative) (originally for PPM)
    p.use_steepening(False) # use contact steepening (originally for PPM)
    p.use_upwindTVD(False) # use upwind biased TVD slope for PPM (need nguard=6)
    p.RiemannSolver("hllc") # Roe, HLL, HLLC, LLF, Marquina, hybrid
    p.entropy(False) # Entropy fix for the Roe solver
    p.shockDetect(False) # Shock Detect for numerical stability
    p.use_hybridOrder(True) # Enforce Riemann density jump

# Hydro boundary conditions:
    p.xl_boundary_type("reflect") 
    p.xr_boundary_type("outflow") 
    p.yl_boundary_type("outflow") 
    p.yr_boundary_type("outflow") 
    p.zl_boundary_type("reflect") 
    p.zr_boundary_type("reflect") 


##############################
#                            #
#     INITIAL CONDITIONS     #
#                            #
##############################

    p.sim_targetRadius(200.0e-04) 
    p.sim_targetHeight(20.0e-04) 
    p.sim_vacuumHeight(60.0e-04) 

# Target material defaults set for Aluminum at room temperature:
    p.sim_rhoTarg(2.7) 
    p.sim_teleTarg(290.11375) 
    p.sim_tionTarg(290.11375) 
    p.sim_tradTarg(290.11375) 
    p.ms_targA(26.9815386) 
    p.ms_targZ(13.0) 
    p.ms_targZMin(0.02) 
    p.eos_targEosType("eos_tab") 
    p.eos_targSubType("ionmix4") 
    p.eos_targTableFile("al-imx-003.cn4") 

# Chamber material defaults set for Helium at pressure 1.6 mbar:
    p.sim_rhoCham(1.0e-06) 
    p.sim_teleCham(290.11375) 
    p.sim_tionCham(290.11375) 
    p.sim_tradCham(290.11375) 
    p.ms_chamA(4.002602) 
    p.ms_chamZ(2.0) 
    p.eos_chamEosType("eos_tab") 
    p.eos_chamSubType("ionmix4") 
    p.eos_chamTableFile("he-imx-005.cn4") 


###########################
#                         #
#     TIME PARAMETERS     #
#                         #
###########################
    p.tstep_change_factor(1.10) 
    p.cfl(0.4) 
    p.dt_diff_factor(1.0e+100) # Disable diffusion dt
    p.rt_dtFactor(1.0e+100) 
    p.hx_dtFactor(1.0e+100) 
    p.tmax(2.0e-09) 
    p.dtmin(1.0e-16) 
    p.dtinit(1.0e-15) 
    p.dtmax(3.0e-09) 
    p.nend(10000000) 


###########################
#                         #
#     MESH PARAMETERS     #
#                         #
###########################
    p.geometry("cylindrical") 

# Domain size:
    p.xmin(0.0) 
    p.xmax(40.0e-04) 
    p.ymin(0.0e-04) 
    p.ymax(80.0e-04) 

# Total number of blocks:
    p.nblockx(1) 
    p.nblocky(2) 

    p.lrefine_max(4) 
    p.lrefine_min(1) 
    p.refine_var_1("dens") 
    p.refine_var_2("tele") 

