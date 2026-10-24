#!/bin/bash
# Login node after both productions: one tarball of checkpoints, probe outputs and logs, with SHA-256 sums.
set -euo pipefail
ROOT=/scratch/junbotong/qoi-srv-20261024
V="$ROOT/analysis/server_runs_20261024/vanda"
cd "$V"
tar -czf results_srv_20261024.tar.gz checkpoints probe logs inputs/MANIFEST.tsv
sha256sum results_srv_20261024.tar.gz > SHA256SUMS
cat SHA256SUMS
echo COLLECT_DONE
