#!/bin/bash
set -e
cd /scratch/junbotong/qoi-mechanism-20260908
source /etc/profile >/dev/null 2>&1
module load Python/3.12.3-GCCcore-13.3.0
venv/bin/python -m pip install -r requirements.txt > logs/install.log 2>&1
venv/bin/python -m pip freeze > logs/pip_freeze.txt
venv/bin/python -m pip check >> logs/install.log 2>&1
touch INSTALL_COMPLETE
