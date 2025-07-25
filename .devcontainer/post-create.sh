#!/bin/bash
set -e

echo "--- Starting Post-Container-Creation Setup ---"

# Fix socket permissions and file line endings
sudo chgrp docker /var/run/docker.sock
sudo dos2unix ./scripts/build-kernel.sh
if [ -f ./scripts/build-images.sh ]; then
    sudo dos2unix ./scripts/build-images.sh
fi

# Kernel build (all build failures visible)
echo "--- Building project kernel... ---"
if ! bash ./scripts/build-kernel.sh; then
    echo "(!) Kernel build failed -- see above for details."
    exit 1
fi

# (Optional) Build images
echo "--- Building project container images... ---"
if [ -f ./scripts/build-images.sh ]; then
    if ! bash ./scripts/build-images.sh; then
        echo "(!) Image build failed (optional step, continue anyway)"
    fi
else
    echo "(!) build-images.sh not found -- skipping container images build."
fi

echo "--- Project Setup Complete ---"
