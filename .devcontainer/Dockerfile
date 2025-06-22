# Use the official dev containers base image for Ubuntu 22.04
FROM mcr.microsoft.com/devcontainers/base:ubuntu-22.04

# Install essential system dependencies for BPF development, Rust, Go, and Python.
# Using LLVM/Clang 18 as it is a recent, stable version well-suited for eBPF development.
# libbpf-dev and libelf-dev are required by user-space loaders and tooling.
# linux-headers-generic provides kernel headers needed for some eBPF operations and tools like bpftool.
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    build-essential libssl-dev pkg-config python3-dev python3.10-venv \
    clang-18 llvm-18 llvm-18-dev libclang-18-dev libpolly-18-dev \
    libbpf-dev libelf-dev zlib1g-dev linux-tools-generic linux-headers-generic \
    curl git golang-go \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Switch to the non-root 'vscode' user for better security practices
USER vscode
# Set the primary working directory
WORKDIR /workspace

# Install the Rust toolchain using rustup.
# This installs the 'stable' toolchain by default.
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/home/vscode/.cargo/bin:${PATH}"

# Install the 'nightly' toolchain, which is required by Aya for eBPF compilation.
# Also, pre-install the 'rust-src' component, which is necessary for `-Z build-std`.
# This moves setup from a runtime script into the image build for reliability.
RUN rustup toolchain install nightly \
    && rustup component add rust-src --toolchain nightly

# Install the essential Aya eBPF build tools.
# bpf-linker: The specialized linker for Aya eBPF programs. This is the core fix.
# cargo-generate: A utility for scaffolding new Aya projects from templates.
RUN cargo install bpf-linker
RUN cargo install cargo-generate

# Install the 'uv' Python package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/home/vscode/.local/bin:${PATH}"

# Copy the Python project definition and install dependencies into the image.
# This creates the virtual environment ahead of time.
COPY --chown=vscode:vscode pyproject.toml./
RUN uv venv
RUN uv pip install -e ".[dev]"