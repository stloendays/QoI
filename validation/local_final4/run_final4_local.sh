#!/usr/bin/env bash
# Local, semantics-preserving recovery launcher for the final four external E2E systems.
#
# This script DOES NOT run the current branch's scientific code. It creates/refreshes
# a dedicated checkout pinned to the frozen scientific commit used by the formal
# external validation, then reproduces the same Python/package setup and runs the
# exact formal_external_e2e.py command for each remaining material.

set -uo pipefail

FROZEN_COMMIT="893f931b3045b0b628329db81999c2f439d4e830"
PYTHON_VERSION="3.12.14"
ROOT="${QOI_LOCAL_ROOT:-$HOME/qoi-final4-local}"
REPO="$ROOT/frozen_repo"
VENV="$ROOT/venv"
RESULTS="$ROOT/results"
LOGS="$ROOT/logs"
STATUS="$ROOT/status"
PROVENANCE="$ROOT/provenance"

materials=(
  "03|aflow-Cl1O12Pb5V3_ICSD_203074"
  "09|aflow-B1C1F6K1_ICSD_1194"
  "10|aflow-B6H2O13Sr3_ICSD_262541"
  "16|aflow-Mo3Na1O16P3_ICSD_66877"
)

mkdir -p "$ROOT" "$RESULTS" "$LOGS" "$STATUS" "$PROVENANCE"

log_controller() {
  printf '[%s] %s\n' "$(date -Is)" "$*" | tee -a "$LOGS/controller.log"
}

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "ERROR: required command '$1' was not found." >&2
    exit 2
  fi
}

require_cmd git
require_cmd uv
require_cmd tar

log_controller "Local final-four recovery bootstrap started"
{
  echo "started_at=$(date -Is)"
  echo "hostname=$(hostname)"
  echo "kernel=$(uname -a)"
  echo "frozen_commit=$FROZEN_COMMIT"
  echo "requested_python=$PYTHON_VERSION"
  command -v nproc >/dev/null 2>&1 && echo "nproc=$(nproc)"
} > "$PROVENANCE/host.txt"

if command -v free >/dev/null 2>&1; then free -h > "$PROVENANCE/memory_before.txt" 2>&1 || true; fi
if command -v df >/dev/null 2>&1; then df -h > "$PROVENANCE/disk_before.txt" 2>&1 || true; fi

# Use HTTPS intentionally: the repository is readable without configuring a local
# GitHub SSH deploy key, which avoids mixing this run with server SSH identities.
if [ ! -d "$REPO/.git" ]; then
  log_controller "Cloning QoI into dedicated frozen checkout"
  git clone --no-checkout https://github.com/stloendays/QoI.git "$REPO"
fi

log_controller "Refreshing frozen scientific commit"
git -C "$REPO" fetch --no-tags origin "$FROZEN_COMMIT"
git -C "$REPO" checkout --detach --force "$FROZEN_COMMIT"
actual_commit="$(git -C "$REPO" rev-parse HEAD)"
if [ "$actual_commit" != "$FROZEN_COMMIT" ]; then
  echo "ERROR: checkout mismatch: $actual_commit != $FROZEN_COMMIT" >&2
  exit 3
fi
printf '%s\n' "$actual_commit" > "$PROVENANCE/git_commit.txt"

# Reproduce the formal workflow's Python patch version exactly. uv is used only to
# obtain Python 3.12.14; package installation itself uses pip, matching GitHub Actions.
if [ ! -x "$VENV/bin/python" ] || [ "$("$VENV/bin/python" -c 'import sys; print(".".join(map(str, sys.version_info[:3])))' 2>/dev/null || true)" != "$PYTHON_VERSION" ]; then
  log_controller "Creating Python $PYTHON_VERSION environment"
  rm -rf "$VENV"
  uv venv --python "$PYTHON_VERSION" --seed "$VENV"
fi

actual_python="$("$VENV/bin/python" -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')"
if [ "$actual_python" != "$PYTHON_VERSION" ]; then
  echo "ERROR: Python mismatch: $actual_python != $PYTHON_VERSION" >&2
  exit 4
fi
"$VENV/bin/python" --version | tee "$PROVENANCE/python_version.txt"

log_controller "Installing frozen external E2E requirements with pip"
"$VENV/bin/python" -m pip install --upgrade pip
"$VENV/bin/python" -m pip install -r "$REPO/validation/requirements-external-e2e.txt"
"$VENV/bin/python" -m pip freeze | sort > "$PROVENANCE/pip_freeze.txt"
sha256sum "$REPO/validation/requirements-external-e2e.txt" > "$PROVENANCE/requirements_sha256.txt"

# A second invocation is resumable: successful materials are skipped, while failed
# or interrupted materials are rerun from a clean output directory.
overall=0
for item in "${materials[@]}"; do
  slot="${item%%|*}"
  material="${item#*|}"
  out="$RESULTS/recovery_$slot"
  log="$LOGS/recovery_${slot}_${material}.log"
  status_file="$STATUS/recovery_${slot}_${material}.status"

  if [ -f "$status_file" ] && grep -q '^SUCCESS ' "$status_file"; then
    log_controller "SKIP already-successful slot=$slot material=$material"
    continue
  fi

  rm -rf "$out"
  mkdir -p "$out"
  printf 'RUNNING %s\n' "$(date -Is)" > "$status_file"
  log_controller "START slot=$slot material=$material"

  set +e
  (
    cd "$REPO"
    nice -n 10 "$VENV/bin/python" validation/formal_external_e2e.py \
      --material-id "$material" \
      --codecs zfp,sz3,sperr \
      --output-dir "$out"
  ) > "$log" 2>&1
  rc=$?
  set -e

  "$VENV/bin/python" --version > "$out/python_version.txt" 2>&1 || true
  "$VENV/bin/python" -m pip freeze | sort > "$out/pip_freeze.txt" 2>&1 || true
  sha256sum "$REPO/validation/requirements-external-e2e.txt" > "$out/requirements_sha256.txt" 2>&1 || true
  printf '%s\n' "$FROZEN_COMMIT" > "$out/git_commit.txt"
  printf '%s\n' "$material" > "$out/requested_material.txt"
  printf '%s\n' "$slot" > "$out/recovery_slot.txt"

  if [ "$rc" -eq 0 ]; then
    printf 'SUCCESS %s rc=0\n' "$(date -Is)" > "$status_file"
    log_controller "SUCCESS slot=$slot material=$material"
  else
    printf 'FAILED %s rc=%s\n' "$(date -Is)" "$rc" > "$status_file"
    log_controller "FAILED slot=$slot material=$material rc=$rc (see $log)"
    overall=1
  fi
done

if command -v free >/dev/null 2>&1; then free -h > "$PROVENANCE/memory_after.txt" 2>&1 || true; fi
if command -v df >/dev/null 2>&1; then df -h > "$PROVENANCE/disk_after.txt" 2>&1 || true; fi
printf '%s\n' "$(date -Is)" > "$PROVENANCE/finished_at.txt"

archive="$ROOT/qoi-final4-local-$(date +%Y%m%d-%H%M%S).tar.gz"
tar -czf "$archive" -C "$ROOT" results logs status provenance
log_controller "Packaged current outputs: $archive"

if [ "$overall" -eq 0 ]; then
  log_controller "ALL FOUR MATERIALS COMPLETED SUCCESSFULLY"
else
  log_controller "ONE OR MORE MATERIALS FAILED/INTERRUPTED; rerun this same script to retry only non-successes"
fi

exit "$overall"
