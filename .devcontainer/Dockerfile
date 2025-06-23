# Use the official dev containers base image for Ubuntu 22.04
FROM mcr.microsoft.com/devcontainers/base:ubuntu-22.04

# Install essential system dependencies for BPF development and Python
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends wget software-properties-common gnupg lsb-release \
    # Get and run the LLVM installer script for version 18
    && wget https://apt.llvm.org/llvm.sh \
    && chmod +x llvm.sh \
    && ./llvm.sh 18 \
    && rm llvm.sh \
    # Now install all system dependencies
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

# Install the Rust toolchain and essential eBPF build tools in a single layer
# to reduce image size and potential build failures due to resource exhaustion.
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
    && . "/home/vscode/.cargo/env" \
    && rustup toolchain install nightly \
    && rustup component add rust-src --toolchain nightly \
    && cargo install bpf-linker \
    && cargo install cargo-generate
ENV PATH="/home/vscode/.cargo/bin:${PATH}"

# Copy the Python project definition and install dependencies into the image.
# This creates the virtual environment ahead of time using standard Python tools.
COPY --chown=vscode:vscode pyproject.toml ./
RUN python3 -m venv .venv
RUN . .venv/bin/activate && pip install -e ".[dev]"
