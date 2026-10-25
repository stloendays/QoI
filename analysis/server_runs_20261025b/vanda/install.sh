#!/bin/bash
# Login node, once: venv with the frozen pins, Henkelman Bader 1.05 from the committed source.
set -euo pipefail
ROOT=/scratch/junbotong/qoi-algo-20261025
V="$ROOT/analysis/server_runs_20261025b/vanda"
cd "$V"
set +eu; source /etc/profile >/dev/null 2>&1; set -eu
module load Python/3.12.3-GCCcore-13.3.0
mkdir -p logs
[ -x venv/bin/python ] || python -m venv venv
venv/bin/python -m pip install -q --upgrade pip > logs/install.log 2>&1
venv/bin/python -m pip install -q -r requirements.txt >> logs/install.log 2>&1
venv/bin/python -m pip freeze > logs/pip_freeze.txt
# Bader: the committed reference source, gfortran from the loaded GCCcore toolchain
rm -rf "$V/bader_build"; cp -r "$ROOT/mechanism/independent_bader_20260908/reference_source" "$V/bader_build"
cd "$V/bader_build"
command -v gfortran >/dev/null || module load GCC/13.3.0 >/dev/null 2>&1 || true
sed -i 's/^LINK = -static/LINK =/' makefile.osx_gfortran
make -f makefile.osx_gfortran > "$V/logs/bader_build.log" 2>&1
test -x bader
cd "$V"
venv/bin/python -c "import numpy, numba, zfpy, pysz, hdf5plugin, h5py, pymatgen, spglib, pytest; print('imports ok')" >> logs/install.log
touch INSTALL_COMPLETE
echo INSTALL_COMPLETE
