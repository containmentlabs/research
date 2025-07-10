#!/bin/bash
set -e

echo "--- Starting Post-Container-Creation Setup ---"

# Install essential Rust eBPF tooling
echo "--- Installing eBPF build tools... ---"
cargo install bpf-linker
cargo install cargo-generate

# The Python environment and Rust toolchain are now pre-installed.
# just need to activate the virtual environment for the following script commands.
. .venv/bin/activate

echo "--- Building project kernel... ---"
bash ./scripts/build-kernel.sh

echo "--- Building project container images... ---"
bash ./scripts/build-images.sh

echo "--- Project Setup Complete ---"