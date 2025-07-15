#!/bin/bash
set -e

echo "--- Starting Post-Container-Creation Setup ---"

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
