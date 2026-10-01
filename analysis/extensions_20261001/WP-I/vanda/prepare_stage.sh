#!/bin/bash
# Prepare a self-contained WP-I stage on NUS Vanda login node.
# Usage:
#   bash prepare_stage.sh /path/to/QoI
set -euo pipefail

REPO="${1:-$PWD}"
STAGE="/scratch/junbotong/qoi-wpi-20261001"
WPI="$REPO/analysis/extensions_20261001/WP-I/vanda"
WPG="$REPO/analysis/extensions_20260930/WP-G/vanda"
WPG_RESULT="$REPO/analysis/extensions_20260930/WP-G"

test -d "$REPO/.git"
test -f "$WPI/run_wpi_reference_only.py"
test -f "$WPG/tasks_base.json"
test -f "$WPG/prefetch.py"
test -f "$WPG_RESULT/reference.csv"
test -d "$REPO/mechanism/independent_bader_20260908/reference_source"
test -f "$REPO/validation/qsq_prospective/development_compatibility_smoke.py"

mkdir -p "$STAGE"/{logs,results/checkpoints,temp,inputs,frozen}

cp -f "$WPI"/run_wpi_reference_only.py "$STAGE/"
cp -f "$WPI"/validate_pilot.py "$STAGE/"
cp -f "$WPI"/status.py "$STAGE/"
cp -f "$WPI"/pilot.pbs "$STAGE/"
cp -f "$WPI"/production.pbs "$STAGE/"
cp -f "$WPI"/finalize_vanda.py "$STAGE/"
cp -f "$WPI"/finalize.pbs "$STAGE/"
cp -f "$WPI"/submit_pipeline.sh "$STAGE/"
cp -f "$WPI"/requirements_wpi.txt "$STAGE/"
cp -f "$WPG"/tasks_base.json "$STAGE/"
cp -f "$WPG"/prefetch.py "$STAGE/"
cp -f "$WPG_RESULT"/reference.csv "$STAGE/wpg_reference.csv"
cp -f "$REPO/validation/qsq_prospective/development_compatibility_smoke.py" "$STAGE/frozen/"

rm -rf "$STAGE/reference_source"
cp -a "$REPO/mechanism/independent_bader_20260908/reference_source" "$STAGE/reference_source"

cd "$STAGE"
set +eu; source /etc/profile >/dev/null 2>&1; set -eu
module load Python/3.12.3-GCCcore-13.3.0
export OMP_NUM_THREADS=1 NUMBA_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1

test -x venv/bin/python || python -m venv venv
venv/bin/python -m pip install -q -r requirements_wpi.txt > logs/install.log 2>&1
venv/bin/python -m pip freeze > logs/pip_freeze.txt

(cd reference_source && make -f makefile.lnx_ifort > ../logs/build_bader.log 2>&1)
test -x reference_source/bader
sha256sum reference_source/bader > logs/bader.sha256

# Public Materials Project payloads; CHGCAR is verified against the frozen hash,
# AECCAR hashes are written into tasks.json by the inherited WP-G prefetcher.
venv/bin/python prefetch.py > logs/prefetch.log 2>&1

venv/bin/python - <<'PY'
import csv, json
from pathlib import Path
root = Path(".")
tasks = json.loads((root/"tasks.json").read_text())
ids = [x for x in (root/"material_ids.txt").read_text().splitlines() if x]
refs = list(csv.DictReader((root/"wpg_reference.csv").open()))
assert len(tasks) == 53
assert len(ids) == 53
assert len(refs) == 53
assert {r["material_id"] for r in refs} == set(tasks)
for m,t in tasks.items():
    assert t.get("aeccar0_sha256") and t.get("aeccar2_sha256")
print("WP-I STAGE_VALIDATED", len(tasks))
PY

git -C "$REPO" rev-parse HEAD > SOURCE_COMMIT
touch PREPARED
echo "WP-I PREPARED at $STAGE"
