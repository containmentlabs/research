# Use the official dev containers base image for Ubuntu 22.04
FROM mcr.microsoft.com/devcontainers/base:ubuntu-22.04

# Passwordless sudo. Use for research use only
RUN echo 'vscode ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers.d/99-vscode

# Install essential system dependencies for BPF, Rust, Go, and Git
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends wget software-properties-common gnupg lsb-release \
    && wget https://apt.llvm.org/llvm.sh \
    && chmod +x llvm.sh \
    && ./llvm.sh 18 \
    && rm llvm.sh \
    && apt-get -y install --no-install-recommends \
    build-essential libssl-dev pkg-config python3-dev python3.10-venv \
    clang-18 llvm-18 llvm-18-dev libclang-18-dev libpolly-18-dev \
    libbpf-dev libelf-dev zlib1g-dev linux-tools-generic linux-headers-generic \
    curl git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ---- GO INSTALL (latest 1.23.0 for go.mod) ----
ENV GO_VERSION 1.23.0
RUN wget https://golang.org/dl/go${GO_VERSION}.linux-amd64.tar.gz \
    && tar -C /usr/local -xzf go${GO_VERSION}.linux-amd64.tar.gz \
    && rm go${GO_VERSION}.linux-amd64.tar.gz
ENV PATH="/usr/local/go/bin:${PATH}"

# Switch to the non-root 'vscode' user
USER vscode
WORKDIR /workspace

# ---- RUST ----
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
    && . "/home/vscode/.cargo/env" \
    && rustup toolchain install nightly \
    && rustup component add rust-src --toolchain nightly \
    && cargo install bpf-linker \
    && cargo install cargo-generate
ENV PATH="/home/vscode/.cargo/bin:${PATH}"

COPY --chown=vscode:vscode pyproject.toml ./
RUN python3 -m venv .venv
RUN . .venv/bin/activate && pip install --default-timeout=600 -e ".[dev]"

# Automatically activate Python venv in new terminals
RUN echo 'source /workspace/.venv/bin/activate' >> /home/vscode/.bashrc

