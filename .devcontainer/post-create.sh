#!/bin/bash
set -e

echo "--- Starting Post-Container-Creation Setup ---"

# The Python environment and Rust toolchain (including bpf-linker) are now pre-installed in the image.
# We just need to activate the virtual environment for the following script commands.
..venv/bin/activate

echo "--- Building project kernel... ---"
bash./scripts/build-kernel.sh

echo "--- Building project container images... ---"
bash./scripts/build-images.sh

echo "--- Project Setup Complete ---"