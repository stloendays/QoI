#!/usr/bin/env bash
set -euo pipefail

STAGING_ROOT="/scratch/junbotong/qoi-ffcz-20261012"
ARCHIVE="${STAGING_ROOT}/results_raw_checkpoints.tar.gz"

tar -czf "${ARCHIVE}" -C "${STAGING_ROOT}" results_raw checkpoints
(
  cd "${STAGING_ROOT}"
  sha256sum "$(basename "${ARCHIVE}")" > SHA256SUMS
  while IFS= read -r -d '' file; do
    sha256sum "${file#${STAGING_ROOT}/}"
  done < <(find "${STAGING_ROOT}/results_raw" "${STAGING_ROOT}/checkpoints" -type f -print0 | sort -z)
) >> "${STAGING_ROOT}/SHA256SUMS"
