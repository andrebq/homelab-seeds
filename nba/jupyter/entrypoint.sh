#!/bin/bash
set -e

BASE_VENV=/opt/jupyter-base
USER_VENV=/var/jupyter-data/.venv

PYVER=$(python3 -c "import sys; print(f'python{sys.version_info.major}.{sys.version_info.minor}')")

# Create the user venv on first run
if [ ! -d "$USER_VENV" ]; then
    uv venv "$USER_VENV"
fi

# Overlay: inject base packages into the user venv via a .pth file.
# Written on every start so it stays correct after image upgrades.
echo "$BASE_VENV/lib/$PYVER/site-packages" \
    > "$USER_VENV/lib/$PYVER/site-packages/_base_overlay.pth"

# Register the kernel pointing at the user venv's Python so that packages
# installed by the user (uv pip install …) are available in notebooks.
# ipykernel itself is visible via the overlay above.
"$USER_VENV/bin/python" -m ipykernel install \
    --prefix "$BASE_VENV" \
    --name python3 \
    --display-name "Python 3 (uv)"

# Default uv operations to the user venv; keep the download cache in the
# volume so reinstalling the container doesn't re-download everything.
export VIRTUAL_ENV="$USER_VENV"
export UV_CACHE_DIR="/var/jupyter-data/.uv-cache"
export PATH="$USER_VENV/bin:$BASE_VENV/bin:$PATH"

exec "$@"
