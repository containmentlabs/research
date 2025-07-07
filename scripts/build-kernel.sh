#!/bin/bash

# /workspace/scripts/build-kernel.sh
set -e

echo "Building L.O.C.K. kernel..."

cd kernel/aya

# The nightly toolchain and rust-src component are now part of the base devcontainer image.
# No installation is needed here.

echo "Building eBPF program..."
# The xtask command will now succeed because the environment is correctly configured
# with bpf-linker and a.cargo/config.toml file that instructs cargo to use it.
if cargo xtask build-ebpf --release; then
    echo "eBPF program built successfully using xtask"
else
    echo "xtask failed, attempting to build directly..."
    # This fallback is also more likely to succeed now.
    cd lock-ebpf
    cargo +nightly build --target bpfel-unknown-none -Z build-std=core,alloc --release
    cd ..
fi

echo "Building user-space loader..."
cargo build --release

echo "Building Go loader..."
cd ../loader
go mod tidy
go build -o lock-loader .

echo "L.O.C.K. kernel build complete!"
echo ""
echo "Binaries:"
echo "  - eBPF program: kernel/aya/target/bpfel-unknown-none/release/lock"
echo "  - Rust loader: kernel/aya/target/release/lock"
echo "  - Go loader: kernel/loader/lock-loader"