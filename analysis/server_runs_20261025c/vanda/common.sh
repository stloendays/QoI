# sourced by every PBS script
ROOT=/scratch/junbotong/qoi-algo2-20261025
V="$ROOT/analysis/server_runs_20261025c/vanda"
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
mkdir -p "$V/checkpoints/sfp" "$V/checkpoints/v" "$V/checkpoints/trunc" "$V/checkpoints/w1" "$V/logs" "$V/probe" "$NUMBA_CACHE_DIR"
sfp_one() {
    "$PY" "$ROOT/analysis/sfp_spin_writer_20261025/run_sfp.py" --material "$1" --inputs "$V/inputs/sfp" \
        --checkpoints "$V/checkpoints/sfp" --repo-root "$ROOT" --frozen-root "$FROZEN" > "$V/logs/sfp_$1.log" 2>&1
}
v_one() {
    "$PY" "$ROOT/analysis/archive_w2_20261025/run_archive_w2.py" --task-id "$1" --inputs "$V/inputs/arch" \
        --checkpoints "$V/checkpoints/v" --repo-root "$ROOT" --frozen-root "$FROZEN" --bader "$BADER" > "$V/logs/v_$1.log" 2>&1
}
fix_one() {
    for s in trunc w1; do
        "$PY" "$ROOT/analysis/archive_partition_fix_20261025/run_fix.py" --study "$s" --task-id "$1" --inputs "$V/inputs/arch" \
            --checkpoints "$V/checkpoints/$s" --repo-root "$ROOT" --frozen-root "$FROZEN" --bader "$BADER" \
            > "$V/logs/fix_${s}_$1.log" 2>&1 || true
    done
}
export ROOT V PY BADER FROZEN
export -f sfp_one v_one fix_one
