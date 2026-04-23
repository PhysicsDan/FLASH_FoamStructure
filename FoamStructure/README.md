This repo contains a modified version of the LaserSlab example provided with FLASH4.8. The `pySimulation.py` file has been modified such that it is possible to initialise any spatial density distribution of choice by reading in a numpy `.npz` file.

TODO:
- [X] 2D density structure from file
- [ ] 3D density structure from file
- [ ] Check that EOS is correctly atributed to the correct layers when using a file to initialise density profile
- [ ] Freeze motion of cells until the surrounding cells are heated to stop unphysical target expansion/homogenisation



# Files
## `simConfig.py`
In this file you can define the target parameters (species, geometry, eos etc.). The geometry can be defined as a simple slab or by pointing to a numpy `.npz` file. More details in [Defining Targets](#defining-targets).

Make sure this file is in your run directory (the same one as `flashPar.py`). Note currently it isn't copied by the setup script so you'll have to move it manually (TODO).

# Usage
Place this folder in
```sh
FLASH4.8/source/Simulation/SimulationMain/python/
```

Run this BEFORE calling the FLASH setup script.
```sh
python generateConfig.py
```
This will generate a `Config` using the `flashPar.py` file in the same directory.

Then run the setup command
```sh
cd FLASH4.8
./setup python/FoamStructure
```
As standard build the `flash4` binary with `cmake` and `make`
```bash
mkdir -p $HOME/Documents/Simulations/flash/flash_test
cd $HOME/Documents/Simulations/flash/flash_test

cmake $HOME/Documents/Simulations/FLASH4.8/object
make -j 16
```

And launch the simulation with
```sh
mpirun -n 64 ./flash4
```

## Custom flashPar Parameters

# Defining Targets

## Simple multilayer slabs
Define target layers as a list of dicts. Layers stack sequentially
in the y-direction: vacuum -> layer[0] -> layer[1] -> ...
The chamber (cham) species is always present as the background fill.
```
Each layer dict MUST contain:
  name     : 4 char species name (e.g. "tar1")
  rho      : initial density [g/cc]
  tele     : initial electron temperature [K]
  tion     : initial ion temperature [K]
  trad     : initial radiation temperature [K]
  A        : atomic mass
  Z        : atomic number
  zMin     : minimum zbar (necessary for laser absorption)
  height   : layer thickness in y-direction [cm]
  radius   : layer radial extent [cm]
  eosType  : EOS type string ("eos_tab" or "eos_gam")
  eosSubType: EOS sub-type string (e.g. "ionmix4")
  eosFile  : EOS table filename
  opAbsorb : opacity absorption model (e.g. "op_tabpa")
  opEmiss  : opacity emission model (e.g. "op_tabpe")
  opTrans  : opacity transport model (e.g. "op_tabro")
  opFileType: opacity file type (e.g. "ionmix4")
  opFileName: opacity table filename
```
See [simConfig](./simConfig.py) for an example of a two layer target

## Custom density maps from numpy
The density profile can also be read from a `numpy` `.npz` file by setting the following variables in `simConfig.py`
```python
CUSTOM_DENS_MAP = True
CUSTOM_DENS_MAP_FILE = "density_map.npz"
```

### File Structure
```
   x       : 1D numpy array of x (radial) cell-centre coordinates [cm]
   y       : 1D numpy array of y (axial) cell-centre coordinates [cm]
   density : 2D nunpy array shape (len(x), len(y)) of density values [g/cc]
   species : 2D numpy array shape (len(x), len(y)) of integer species indices
             (0 = cham, 1 = first layer, 2 = second layer, ...)
```
To generate the `.npz` file from these arrays
```python
np.savez("density_map.npz", x=x, y=y, density=density, species=species)
```


## Unphysical Target Expansion
FLASH currently doesn't support negative pressures in the EOS, therefore, the plasma will expand unphysically even when not irradiated by a laser. One trick to prevent this is to use `BDRY_VAR` to freeze portions of the simulation domain until the surrounding cells heat up to a desired amount. When `BDRY_VAR=1` the cells are frozen and `BDRY_VAR=-1` the cells behave as a fluid.

### Current Implementation
When `USE_BDRY` is `True`, target cells are initialised as frozen (`BDRY_VAR = 1.0`) and only unfrozen when a nearby *unfrozen* cell exceeds `BDRY_TEMP_THRESHOLD`. This prevents unphysical pre-expansion of solid targets before they are heated by the laser.
```
BDRY_VAR =  1.0  -> frozen (rigid body, reflecting boundary)
BDRY_VAR = -1.0  -> active (normal fluid)
```
The check uses a spatial search: for each frozen cell, if any unfrozen cell within `BDRY_UNFREEZE_DIST [cm]` has electron temperature above `BDRY_TEMP_THRESHOLD [K]`, the frozen cell is released. Unfreezing propagates inward from the heated surface.
```
USE_BDRY = True
BDRY_TEMP_THRESHOLD = 1000.0       # [K] electron temperature threshold
BDRY_UNFREEZE_DIST  = 5.0e-04      # [cm] search radius for hot neighbours
```
These values are set in [`simConfig.py`](./simConfig.py)
