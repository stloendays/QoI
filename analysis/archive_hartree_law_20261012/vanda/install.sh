#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"
set +e
source /etc/profile >/dev/null 2>&1
set -e
module load Python/3.12.3-GCCcore-13.3.0
mkdir -p logs inputs checkpoints
if [ ! -x venv/bin/python ]; then
    python -m venv venv
fi
venv/bin/python -m pip install -q -r requirements.txt > logs/install.log 2>&1
venv/bin/python -m pip freeze > logs/pip_freeze.txt
touch INSTALL_COMPLETE
echo INSTALL_COMPLETE
