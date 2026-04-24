# ── Compiler discovery via MPI wrappers ───────────────────────────────────────
set(MPI_DIR "$ENV{CONDA_PREFIX}")
set(CMAKE_Fortran_COMPILER  ${MPI_DIR}/bin/mpif90)
set(CMAKE_C_COMPILER        ${MPI_DIR}/bin/mpicc)
set(CMAKE_CXX_COMPILER      ${MPI_DIR}/bin/mpicxx)
set(CMAKE_EXE_LINKER_FLAGS "-Wl,-no_compact_unwind")
set(CMAKE_SHARED_LINKER_FLAGS "-Wl,-no_compact_unwind")

# ── Tell OpenMPI wrappers which underlying compilers to use ──────────────────
# Critical on Apple Silicon — prevents wrappers falling back to /usr/bin/clang
set(ENV{OMPI_CC}  ${MPI_DIR}/bin/arm64-apple-darwin20.0.0-clang)
set(ENV{OMPI_CXX} ${MPI_DIR}/bin/arm64-apple-darwin20.0.0-clang++)
set(ENV{OMPI_FC}  ${MPI_DIR}/bin/gfortran)

# ── Library/header search paths ───────────────────────────────────────────────
set(PYBIND11_DIR "$ENV{CONDA_PREFIX}")
set(HDF5_DIR     "$ENV{CONDA_PREFIX}")
set(HYPRE_DIR    "$ENV{CONDA_PREFIX}")

# Helps CMake find libs under $CONDA_PREFIX/lib and headers under include/
list(APPEND CMAKE_PREFIX_PATH "$ENV{CONDA_PREFIX}")

# Find gfortran's include dir for ISO_Fortran_binding.h
execute_process(
    COMMAND ${MPI_DIR}/bin/gfortran -print-file-name=include
    OUTPUT_VARIABLE GFORTRAN_INCLUDE_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
)

# ── Compiler flags ────────────────────────────────────────────────────────────
set(FFLAGS  "-ffree-line-length-0 -fdefault-real-8 -fdefault-double-8 -fallow-argument-mismatch")
set(CFLAGS  "-arch arm64 -idirafter ${GFORTRAN_INCLUDE_DIR}")
set(CXXFLAGS "-arch arm64 -idirafter ${GFORTRAN_INCLUDE_DIR}")
