# sourced by every PBS script
ROOT=/scratch/junbotong/qoi-xcl-20261025
V="$ROOT/analysis/server_runs_20261025/vanda"
PY="$V/venv/bin/python"
FROZEN="$ROOT/frozen"
cd "$ROOT"
set +eu; source /etc/profile >/dev/null 2>&1; set -eu
module load Python/3.12.3-GCCcore-13.3.0
export OMP_NUM_THREADS=1 NUMBA_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
test -f "$V/INSTALL_COMPLETE"
test -f "$V/PREFETCH_COMPLETE"
mkdir -p "$V/checkpoints/xcl" "$V/logs" "$V/probe"
xcl_one() {
    "$PY" "$ROOT/analysis/xc_linearized_law_20261025/run_xcl.py" --material "$1" --inputs "$V/inputs/xc"         --checkpoints "$V/checkpoints/xcl" --repo-root "$ROOT" --frozen-root "$FROZEN" > "$V/logs/xcl_$1.log" 2>&1
}
export ROOT V PY FROZEN
export -f xcl_one
