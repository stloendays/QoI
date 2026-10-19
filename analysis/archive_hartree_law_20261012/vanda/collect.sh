#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"
test -d checkpoints
tar -czf archive_law_checkpoints.tar.gz checkpoints
sha256sum archive_law_checkpoints.tar.gz > SHA256SUMS
sha256sum checkpoints/*.json >> SHA256SUMS
echo "WROTE archive_law_checkpoints.tar.gz and SHA256SUMS"
