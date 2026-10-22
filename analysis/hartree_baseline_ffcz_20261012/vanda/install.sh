#!/usr/bin/env bash
set -euo pipefail

STAGING_ROOT="/scratch/junbotong/qoi-ffcz-20261012"
CODE_DIR="${STAGING_ROOT}/analysis/hartree_baseline_ffcz_20261012"
SRC_DIR="${STAGING_ROOT}/FFCz"
BUILD_DIR="${STAGING_ROOT}/ffcz-build"
BIN_DIR="${STAGING_ROOT}/bin"
VENV_DIR="${STAGING_ROOT}/venv"
BUILD_LOG="${STAGING_ROOT}/build.log"

mkdir -p "${STAGING_ROOT}" "${BIN_DIR}"
module load Python/3.12.3-GCCcore-13.3.0
module load CMake/3.29.3-GCCcore-13.3.0
module load FFTW/3.3.10-GCC-13.3.0
module load zstd/1.5.6-GCCcore-13.3.0

{
  echo "modules:"
  module list 2>&1
  echo "python: $(command -v python)"
  python --version
  echo "cmake: $(command -v cmake)"
  cmake --version | head -n 1
  echo "pkg-config:"
  pkg-config --modversion fftw3 fftw3f libzstd
} > "${BUILD_LOG}"

if [[ ! -d "${VENV_DIR}" ]]; then
  python -m venv "${VENV_DIR}"
fi
"${VENV_DIR}/bin/python" -m pip install --upgrade pip >> "${BUILD_LOG}" 2>&1
"${VENV_DIR}/bin/python" -m pip install -r "${CODE_DIR}/vanda/requirements.txt" >> "${BUILD_LOG}" 2>&1

if [[ ! -d "${SRC_DIR}/.git" ]]; then
  git clone https://github.com/rcrcarissa/FFCz.git "${SRC_DIR}" >> "${BUILD_LOG}" 2>&1
fi
git -C "${SRC_DIR}" fetch --quiet --tags origin >> "${BUILD_LOG}" 2>&1
git -C "${SRC_DIR}" checkout --detach 96649b36b2a155075682d86fbabeb925e7d9e29a >> "${BUILD_LOG}" 2>&1

FFTW_ROOT_VALUE="${FFTW_ROOT:-${EBROOTFFTW:-}}"
ZSTD_ROOT_VALUE="${ZSTD_ROOT:-${EBROOTZSTD:-}}"
export PKG_CONFIG_PATH="${FFTW_ROOT_VALUE:+${FFTW_ROOT_VALUE}/lib/pkgconfig:}${ZSTD_ROOT_VALUE:+${ZSTD_ROOT_VALUE}/lib/pkgconfig:}${PKG_CONFIG_PATH:-}"
export LD_LIBRARY_PATH="${FFTW_ROOT_VALUE:+${FFTW_ROOT_VALUE}/lib:}${ZSTD_ROOT_VALUE:+${ZSTD_ROOT_VALUE}/lib:}${LD_LIBRARY_PATH:-}"
pkg-config --exists fftw3 fftw3f libzstd >> "${BUILD_LOG}" 2>&1

cmake -S "${SRC_DIR}/CPU" -B "${BUILD_DIR}" -DCMAKE_BUILD_TYPE=Release >> "${BUILD_LOG}" 2>&1
cmake --build "${BUILD_DIR}" --target ffcz_cpu -j "${PBS_NCPUS:-8}" >> "${BUILD_LOG}" 2>&1
cp "${BUILD_DIR}/ffcz_cpu" "${BIN_DIR}/ffcz_cpu"
chmod +x "${BIN_DIR}/ffcz_cpu"

set +e
"${BIN_DIR}/ffcz_cpu" > "${STAGING_ROOT}/ffcz_cpu.usage.txt" 2>&1
USAGE_RC=$?
set -e
printf 'usage_rc=%s\n' "${USAGE_RC}" >> "${BUILD_LOG}"
sha256sum "${BIN_DIR}/ffcz_cpu" | tee "${STAGING_ROOT}/ffcz_cpu.sha256" >> "${BUILD_LOG}"
git -C "${SRC_DIR}" rev-parse HEAD | tee "${STAGING_ROOT}/ffcz_commit.txt" >> "${BUILD_LOG}"
printf 'INSTALL_COMPLETE\n' > "${STAGING_ROOT}/INSTALL_COMPLETE"
