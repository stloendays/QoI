#!/bin/bash
# Login node after all productions: one tarball of checkpoints, probe outputs and logs, with SHA-256 sums.
set -euo pipefail
ROOT=/scratch/junbotong/qoi-algo2-20261025
V="$ROOT/analysis/server_runs_20261025c/vanda"
cd "$V"
tar -czf results_algo2_20261025.tar.gz checkpoints probe logs inputs/MANIFEST.tsv
sha256sum results_algo2_20261025.tar.gz > SHA256SUMS
cat SHA256SUMS
echo COLLECT_DONE
