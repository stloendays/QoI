#!/bin/bash
# Vanda login node: Python 3.12.3 module + the frozen pins (as mechanism/independent_bader_20260908), Henkelman Bader 1.05 build.
set -e
cd "$(dirname "$0")"
set +e; source /etc/profile >/dev/null 2>&1; set -e
module load Python/3.12.3-GCCcore-13.3.0
mkdir -p logs results temp
test -x venv/bin/python || python -m venv venv
venv/bin/python -m pip install -q -r requirements.txt > logs/install.log 2>&1
venv/bin/python -m pip freeze > logs/pip_freeze.txt
(cd reference_source && make -f makefile.lnx_ifort > ../logs/build_bader.log 2>&1 && test -x bader)
sha256sum reference_source/bader > logs/bader.sha256
touch INSTALL_COMPLETE
echo INSTALL_COMPLETE
