#!/bin/bash
set -e

echo "Building L.O.C.K. kernel..."

cd kernel/aya

echo "Installing nightly Rust toolchain..."
rustup toolchain install nightly

echo "Installing rust-src component for building std..."
rustup component add rust-src --toolchain nightly

echo "Building eBPF program..."
if cargo xtask build-ebpf --release 2>/dev/null; then
    echo "eBPF program built successfully using xtask"
else
    echo "xtask failed, building directly..."
    cd lock-ebpf
    cargo +nightly build --target bpfel-unknown-none -Zbuild-std=core --release
    cd ..
fi

echo "Building user-space loader..."
cargo build --release

echo "Building Go loader..."
cd ../loader
go build -o lock-loader .

echo "L.O.C.K. kernel build complete!"
echo ""
echo "Binaries:"
echo "  - eBPF program: kernel/aya/target/bpfel-unknown-none/release/lock"
echo "  - Rust loader: kernel/aya/target/release/lock"
echo "  - Go loader: kernel/loader/lock-loader" 