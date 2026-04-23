#!/bin/zsh -e
FLASH_DIR="/Users/dmolloy/Documents/Simulations/FLASH4.8"
SIM_DIR="/Users/dmolloy/Documents/Simulations/flash/flash_test"

echo "Activating python env"
source "$(brew --prefix)/Caskroom/miniconda/base/etc/profile.d/conda.sh"
conda activate flash

echo "Generating config file"
cd "$FLASH_DIR/source/Simulation/SimulationMain/python/LaserSlabFoam/FoamStructure"
python generateConfig.py

echo "Running setup"
cd "$FLASH_DIR"
./setup python/LaserSlabFoam/FoamStructure --site=daniel.macos

echo "Compiling executable"
cd "$SIM_DIR"
rm -rf *
cmake "$FLASH_DIR/object"
make -j 16
