# General FLASH info
Note: view [this README](./FoamStructure/README.md) for more info on the specific modifications to the LaserSlab setup.


Flash4.8 comes with a python wrapper which makes modifying the code much easier.

Additional docs:

- [PyFlash](https://flash.rochester.edu/site/flashcode/user_support/pyFlashDocs_py/index.html)
- [Flash](https://flash.rochester.edu/site/flashcode/user_support.html)
- [Hypre](https://hypre.readthedocs.io/en/latest/ch-intro.html)
- Search the Mailing List: `site:"https://flash.rochester.edu/pipermail/flash-users/" laserslab`

## Building FLASH
### Dependencies
I have tested the following versions
```sh
hdf5=1.14.4
cmake=3.29.2
lapack=3.12.0
blas=3.12.0
hypre=2.32.9
gcc=14.1.0
```

#### Building HYPRE from Source
```bash
cd $HOME/src/hypre
git checkout v2.33.0

```
Build it with `cmake`
```bash
cd $HOME/src/hypre/src
cmake . -B cmbuild/ -DHYPRE_ENABLE_SHARED=ON -DCMAKE_C_FLAGS="-fPIC" -DCMAKE_CXX_FLAGS="-fPIC"

cd cmbuild
make -j16
make install
```

#### Building pyFLASH
```bash
conda create -n pyflash -c conda-forge pybind11 python=3.10 numpy scipy
```

To use my modified version you also need `scipy`

Activate the env
`conda activate pyflash`

1. Building the `flash4` binary
   
Note, you will need to make a folder for your HPC with `Makefile.H` and `cmake.site` in `FLASH4.8/sites/` if there isn't already one present. Run `hostname` to check what the folder should be called (e.g. `kelvin2.alces.network`)

To build the LaserSlab example with the Python wrapper

```bash
cd FLASH4.8
./setup python/LaserSlab
```

I like to create a separate folder to run my simulations
```bash
mkdir ~/flash_run
cd ~/flash_run

cmake $HOME/FLASH4.8/object
```
Then
```bash
make -j 16
```
You should now have a `flash4` binary in this folder! If you have issues make sure to remove the contents of the `build` directory before trying again.

The folder should look something like
```bash
 B-2330-clipped.cn4
 B-opac.cn4
 CH2-7173-50meV.cn4
 CH2-opac.cn4
 flash
 flash4
 flashPar.py
 he-imx-005.cn4
 He-opac.cn4
 '*.imx'
 pySimulation.py
 run.batch
```

## TODO - Parallelisation
FLASH can be parallised with mpi and openmp. I need to do some testing on what is the best option.

See pg. 621 - `threadRayTrace=True` and `threadBlockList`
