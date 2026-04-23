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

#########################################
#                                       #
#     BDRY (FREEZE) OPTIONS             #
#                                       #
#########################################
# When USE_BDRY is True, target cells are initialised as frozen
# (BDRY_VAR = 1.0) and only unfrozen when a nearby *unfrozen* cell
# exceeds BDRY_TEMP_THRESHOLD. This prevents unphysical pre-expansion
# of solid targets before they are heated by the laser.
#
# BDRY_VAR =  1.0  -> frozen (rigid body, reflecting boundary)
# BDRY_VAR = -1.0  -> active (normal fluid)
#
# The check uses a spatial search: for each frozen cell, if any
# unfrozen cell within BDRY_UNFREEZE_DIST [cm] has electron
# temperature above BDRY_TEMP_THRESHOLD [K], the frozen cell is
# released. Unfreezing propagates inward from the heated surface.
USE_BDRY = True
BDRY_TEMP_THRESHOLD = 1000.0       # [K] electron temperature threshold
BDRY_UNFREEZE_DIST  = 5.0e-04      # [cm] search radius for hot neighbours
