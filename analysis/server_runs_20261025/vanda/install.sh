#!/bin/bash
# Login node, once: venv with the frozen pins (same requirements as the 2026-10-24 server runs).
set -euo pipefail
ROOT=/scratch/junbotong/qoi-xcl-20261025
V="$ROOT/analysis/server_runs_20261025/vanda"
cd "$V"
set +eu; source /etc/profile >/dev/null 2>&1; set -eu
module load Python/3.12.3-GCCcore-13.3.0
mkdir -p logs
[ -x venv/bin/python ] || python -m venv venv
venv/bin/python -m pip install -q --upgrade pip > logs/install.log 2>&1
venv/bin/python -m pip install -q -r requirements.txt >> logs/install.log 2>&1
venv/bin/python -m pip freeze > logs/pip_freeze.txt
venv/bin/python -c "import numpy, pandas, zfpy, pysz, pymatgen; print('imports ok')" >> logs/install.log
touch INSTALL_COMPLETE
echo INSTALL_COMPLETE
