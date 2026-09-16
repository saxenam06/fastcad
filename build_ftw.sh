#!/usr/bin/env bash
# Build FloatTetwild_bin, the fTetWild command line tool.
#
# We need the binary rather than the `pytetwild` wheel because only the binary takes `--tag`:
# one integer per input triangle, carried through the meshing onto the output. That turns CAD
# face identity from something recovered afterwards into something inherited — which is the whole
# point, and it comes without TetGen's AGPL licence.
#
#   wsl -e bash -lc "bash /mnt/c/Work/fastcad/build_ftw.sh"
set -euo pipefail

# The user's environments, not /opt/micromamba, which is root-owned and refuses to be written to.
export MAMBA_ROOT_PREFIX=$HOME/.local/share/mamba
eval "$(micromamba shell hook -s bash)"

ENV=ftw
if [ ! -d "$MAMBA_ROOT_PREFIX/envs/$ENV" ]; then
  micromamba create -y -n "$ENV" -c conda-forge \
    cxx-compiler 'cmake<3.30' ninja make gmp mpfr tbb tbb-devel eigen boost-cpp git
else
  micromamba install -y -n "$ENV" -c conda-forge \
    cxx-compiler 'cmake<3.30' ninja make gmp mpfr tbb tbb-devel eigen boost-cpp git
fi

micromamba activate "$ENV"

SRC=$HOME/src/fTetWild
if [ ! -d "$SRC" ]; then
  mkdir -p "$(dirname "$SRC")"
  git clone --depth 1 https://github.com/wildmeshing/fTetWild.git "$SRC"
fi

cd "$SRC"
rm -rf build && mkdir build && cd build

# Its CMake fetches libigl. Recent libigl releases changed the CMake API that fTetWild's
# CMakeLists still calls, which is what broke the first attempt at `igl_include`. Pinning libigl
# to the release fTetWild was written against avoids patching either project.
cmake .. \
  -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DFLOAT_TETWILD_USE_TBB=ON \
  -DLIBIGL_GIT_TAG=v2.4.0 \
  2>&1 | tail -40

ninja -j6 2>&1 | tail -30
ls -lh FloatTetwild_bin && ./FloatTetwild_bin --help 2>&1 | head -40
