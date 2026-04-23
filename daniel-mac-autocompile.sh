#!/bin/zsh -e
FLASH_DIR="/Users/dmolloy/Documents/Simulations/FLASH4.8"
SIM_DIR="/Users/dmolloy/Documents/Simulations/flash/flash_test"

source "$(brew --prefix)/Caskroom/miniconda/base/etc/profile.d/conda.sh"
conda activate flash

cd "$FLASH_DIR"
./setup python/LaserSlabFoam/FoamStructure --site=daniel.macos

cd "$SIM_DIR"
rm -rf *
cmake "$FLASH_DIR/object"
make -j 16
