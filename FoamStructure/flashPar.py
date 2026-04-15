import os

#########################################
#                                       #
#     TARGET LAYER DEFINITIONS          #
#                                       #
#########################################
# Define target layers as a list of dicts. Layers stack sequentially
# in the y-direction: vacuum -> layer[0] -> layer[1] -> ...
# The chamber (cham) species is always present as the background fill.

# Each layer dict MUST contain:
#   name     : short species name (e.g. "tar1") - used in setup line
#   rho      : initial density [g/cc]
#   tele     : initial electron temperature [K]
#   tion     : initial ion temperature [K]
#   trad     : initial radiation temperature [K]
#   A        : atomic mass
#   Z        : atomic number
#   zMin     : minimum zbar (some preionisation necessary for laser absorption)
#   height   : layer thickness in y-direction [cm]
#   radius   : layer radial extent [cm]
#   eosType  : EOS type string ("eos_tab" or "eos_gam")
#   eosSubType: EOS sub-type string (e.g. "ionmix4")
#   eosFile  : EOS table filename
#   opAbsorb : opacity absorption model (e.g. "op_tabpa")
#   opEmiss  : opacity emission model (e.g. "op_tabpe")
#   opTrans  : opacity transport model (e.g. "op_tabro")
#   opFileType: opacity file type (e.g. "ionmix4")
#   opFileName: opacity table filename

LAYERS = [
    {
        "name": "tar1",
        "rho": 2.7,
        "tele": 290.11375,
        "tion": 290.11375,
        "trad": 290.11375,
        "A": 26.9815386,
        "Z": 13.0,
        "zMin": 0.02,
        "height": 20.0e-04,
        "radius": 200.0e-04,
        "eosType": "eos_tab",
        "eosSubType": "ionmix4",
        "eosFile": "al-imx-003.cn4",
        "opAbsorb": "op_tabpa",
        "opEmiss": "op_tabpe",
        "opTrans": "op_tabro",
        "opFileType": "ionmix4",
        "opFileName": "al-imx-003.cn4",
    },
    # Example: uncomment to add a second layer
    {
        "name": "tar2",
        "rho": 1.0,
        "tele": 290.11375,
        "tion": 290.11375,
        "trad": 290.11375,
        "A": 13,
        "Z": 7,
        "zMin": 0.0,
        "height": 10.0e-04,
        "radius": 200.0e-04,
        "eosType": "eos_tab",
        "eosSubType": "ionmix4",
        "eosFile": "polystyrene-imx-001.cn4",
        "opAbsorb": "op_tabpa",
        "opEmiss": "op_tabpe",
        "opTrans": "op_tabro",
        "opFileType": "ionmix4",
        "opFileName": "polystyrene-imx-001.cn4",
    },
]

#########################################
#                                       #
#     CHAMBER (BACKGROUND) DEFINITION   #
#                                       #
#########################################
CHAMBER = {
    "rho": 1.0e-06,
    "tele": 290.11375,
    "tion": 290.11375,
    "trad": 290.11375,
    "A": 4.002602,
    "Z": 2.0,
    "eosType": "eos_tab",
    "eosSubType": "ionmix4",
    "eosFile": "he-imx-005.cn4",
    "opAbsorb": "op_tabpa",
    "opEmiss": "op_tabpe",
    "opTrans": "op_tabro",
    "opFileType": "ionmix4",
    "opFileName": "he-imx-005.cn4",
}

#########################################
#                                       #
#     CUSTOM DENSITY MAP OPTIONS        #
#                                       #
#########################################
# If True, density and species at each cell are read from an external
# .npz file instead of using the geometric layer definitions.
# The .npz file must contain:
#   x       : 1D array of x (radial) cell-centre coordinates [cm]
#   y       : 1D array of y (axial) cell-centre coordinates [cm]
#   density : 2D array shape (len(x), len(y)) of density values [g/cc]
#   species : 2D array shape (len(x), len(y)) of integer species indices
#             (0 = cham, 1 = first layer, 2 = second layer, ...)
CUSTOM_DENS_MAP = False
CUSTOM_DENS_MAP_FILE = "density_map.npz"


def _species_string():
    """Build the species= setup argument from LAYERS."""
    names = ["cham"] + [layer["name"] for layer in LAYERS]
    return "species=" + ",".join(names)


def setupArgs():
    args = [
        "-auto",
        "-2d",
        "+cylindrical",
        "-nxb=16",  # cells per box
        "-nyb=16",  # cells per box
        "+hdf5typeio",
        _species_string(),
        "+mtmmmt",
        "+laser",
        "+uhd3t",
        "+mgd",
        "mgd_meshgroups=6",  # Modify this if using different OPAC tables
        "+python",
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

    # Dynamically add plot vars for each layer species
    # TODO: Check that I can have an unlimited number of plot variables
    plot_idx = 9
    for layer in LAYERS:
        getattr(p, f"plot_var_{plot_idx}")(layer["name"])
        plot_idx += 1

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
    p.rt_mgdBounds_2(1.0e00)
    p.rt_mgdBounds_3(1.0e01)
    p.rt_mgdBounds_4(1.0e02)
    p.rt_mgdBounds_5(1.0e03)
    p.rt_mgdBounds_6(1.0e04)
    p.rt_mgdBounds_7(1.0e05)
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
    p.op_chamAbsorb(CHAMBER["opAbsorb"])
    p.op_chamEmiss(CHAMBER["opEmiss"])
    p.op_chamTrans(CHAMBER["opTrans"])
    p.op_chamFileType(CHAMBER["opFileType"])
    p.op_chamFileName(CHAMBER["opFileName"])

    ### SET TARGET LAYER OPACITY OPTIONS ###
    for layer in LAYERS:
        name = layer["name"]
        getattr(p, f"op_{name}Absorb")(layer["opAbsorb"])
        getattr(p, f"op_{name}Emiss")(layer["opEmiss"])
        getattr(p, f"op_{name}Trans")(layer["opTrans"])
        getattr(p, f"op_{name}FileType")(layer["opFileType"])
        getattr(p, f"op_{name}FileName")(layer["opFileName"])

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
    p.ed_power_1_2(1.0e09)
    p.ed_power_1_3(1.0e09)
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

    p.order(3)  # Interpolation order (first/second/third/fifth order)
    p.slopeLimiter("minmod")  # Slope limiters (minmod, mc, vanLeer, hybrid, limited)
    p.LimitedSlopeBeta(1.0)  # Slope parameter for the "limited" slope by Toro
    p.charLimiting(True)  # Characteristic limiting vs. Primitive limiting
    p.use_avisc(True)  # use artificial viscosity (originally for PPM)
    p.cvisc(0.1)  # coefficient for artificial viscosity
    p.use_flattening(False)  # use flattening (dissipative) (originally for PPM)
    p.use_steepening(False)  # use contact steepening (originally for PPM)
    p.use_upwindTVD(False)  # use upwind biased TVD slope for PPM (need nguard=6)
    p.RiemannSolver("hllc")  # Roe, HLL, HLLC, LLF, Marquina, hybrid
    p.entropy(False)  # Entropy fix for the Roe solver
    p.shockDetect(False)  # Shock Detect for numerical stability
    p.use_hybridOrder(True)  # Enforce Riemann density jump

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

    p.sim_vacuumHeight(60.0e-04)
    p.sim_initGeom("slab")

    # Number of target layers
    p.sim_numLayers(len(LAYERS))

    # Set per-layer parameters
    for idx, layer in enumerate(LAYERS):
        n = idx + 1  # 1-indexed for FLASH parameter naming
        name = layer["name"]

        getattr(p, f"sim_rho_{n}")(layer["rho"])
        getattr(p, f"sim_tele_{n}")(layer["tele"])
        getattr(p, f"sim_tion_{n}")(layer["tion"])
        getattr(p, f"sim_trad_{n}")(layer["trad"])
        getattr(p, f"sim_height_{n}")(layer["height"])
        getattr(p, f"sim_radius_{n}")(layer["radius"])
        getattr(p, f"ms_{name}A")(layer["A"])
        getattr(p, f"ms_{name}Z")(layer["Z"])
        if layer.get("zMin", 0.0) > 0:
            getattr(p, f"ms_{name}ZMin")(layer["zMin"])
        getattr(p, f"eos_{name}EosType")(layer["eosType"])
        getattr(p, f"eos_{name}SubType")(layer["eosSubType"])
        getattr(p, f"eos_{name}TableFile")(layer["eosFile"])

    # Chamber material defaults set for Helium at pressure 1.6 mbar:
    p.sim_rhoCham(CHAMBER["rho"])
    p.sim_teleCham(CHAMBER["tele"])
    p.sim_tionCham(CHAMBER["tion"])
    p.sim_tradCham(CHAMBER["trad"])
    p.ms_chamA(CHAMBER["A"])
    p.ms_chamZ(CHAMBER["Z"])
    p.eos_chamEosType(CHAMBER["eosType"])
    p.eos_chamSubType(CHAMBER["eosSubType"])
    p.eos_chamTableFile(CHAMBER["eosFile"])

    # Custom density map parameters
    p.sim_customDensMap(CUSTOM_DENS_MAP)
    p.sim_densMapFile(CUSTOM_DENS_MAP_FILE)

    ###########################
    #                         #
    #     TIME PARAMETERS     #
    #                         #
    ###########################
    p.tstep_change_factor(1.10)
    p.cfl(0.4)
    p.dt_diff_factor(1.0e100)  # Disable diffusion dt
    p.rt_dtFactor(1.0e100)
    p.hx_dtFactor(1.0e100)
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
