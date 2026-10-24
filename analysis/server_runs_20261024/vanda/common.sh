# sourced by every PBS script
ROOT=/scratch/junbotong/qoi-srv-20261024
V="$ROOT/analysis/server_runs_20261024/vanda"
PY="$V/venv/bin/python"
BADER="$V/bader_build/bader"
FROZEN="$ROOT/frozen"
cd "$ROOT"
set +eu; source /etc/profile >/dev/null 2>&1; set -eu
module load Python/3.12.3-GCCcore-13.3.0
export OMP_NUM_THREADS=1 NUMBA_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
test -f "$V/INSTALL_COMPLETE"
test -f "$V/PREFETCH_COMPLETE"
mkdir -p "$V/checkpoints/arch" "$V/checkpoints/xc" "$V/logs" "$V/probe"
arch_one() {
    "$PY" "$ROOT/analysis/archive_truncation_20261024/run_archive_truncation.py" run --task-id "$1" \
        --inputs "$V/inputs/arch" --checkpoints "$V/checkpoints/arch" --repo-root "$ROOT" --frozen-root "$FROZEN" \
        --bader "$BADER" > "$V/logs/arch_$1.log" 2>&1
}
xc_one() {
    "$PY" "$ROOT/analysis/nonlinear_xc_20261024/run_xc.py" --material "$1" --inputs "$V/inputs/xc" \
        --checkpoints "$V/checkpoints/xc" --repo-root "$ROOT" --frozen-root "$FROZEN" > "$V/logs/xc_$1.log" 2>&1
}
export ROOT V PY BADER FROZEN
export -f arch_one xc_one
