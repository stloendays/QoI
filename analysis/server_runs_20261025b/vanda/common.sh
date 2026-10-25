# sourced by every PBS script
ROOT=/scratch/junbotong/qoi-algo-20261025
V="$ROOT/analysis/server_runs_20261025b/vanda"
PY="$V/venv/bin/python"
BADER="$V/bader_build/bader"
FROZEN="$ROOT/frozen"
cd "$ROOT"
set +eu; source /etc/profile >/dev/null 2>&1; set -eu
module load Python/3.12.3-GCCcore-13.3.0
export OMP_NUM_THREADS=1 NUMBA_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export NUMBA_CACHE_DIR="$V/numba_cache"
test -f "$V/INSTALL_COMPLETE"
test -f "$V/PREFETCH_COMPLETE"
mkdir -p "$V/checkpoints/w1" "$V/checkpoints/arch" "$V/logs" "$V/probe" "$NUMBA_CACHE_DIR"
w1_one() {
    "$PY" "$ROOT/analysis/waterfill_writer_20261025/run_w1.py" --material "$1" --inputs "$V/inputs/w1"         --checkpoints "$V/checkpoints/w1" --repo-root "$ROOT" --frozen-root "$FROZEN" > "$V/logs/w1_$1.log" 2>&1
}
arch_one() {
    "$PY" "$ROOT/analysis/archive_waterfill_20261025/run_archive_w1.py" run --task-id "$1"         --inputs "$V/inputs/arch" --checkpoints "$V/checkpoints/arch" --repo-root "$ROOT" --frozen-root "$FROZEN"         --bader "$BADER" > "$V/logs/arch_$1.log" 2>&1
}
export ROOT V PY BADER FROZEN
export -f w1_one arch_one
