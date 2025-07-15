FROM mcr.microsoft.com/devcontainers/base:ubuntu-22.04

# 1. Passwordless sudo for vscode
RUN echo 'vscode ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers.d/99-vscode

# 2. System dependencies: install wget first, then LLVM repo, then the rest
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends wget software-properties-common gnupg lsb-release \
    && wget https://apt.llvm.org/llvm.sh \
    && chmod +x llvm.sh && ./llvm.sh 18 && rm llvm.sh \
    && apt-get -y install --no-install-recommends \
    build-essential libssl-dev pkg-config python3-dev python3.10-venv \
    clang-18 llvm-18 llvm-18-dev libclang-18-dev libpolly-18-dev \
    libbpf-dev libelf-dev zlib1g-dev linux-tools-generic linux-headers-generic \
    curl git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 3. Go for loader (update go.mod/go code uses 1.23+)
ENV GO_VERSION 1.23.0
RUN wget https://golang.org/dl/go${GO_VERSION}.linux-amd64.tar.gz \
    && tar -C /usr/local -xzf go${GO_VERSION}.linux-amd64.tar.gz \
    && rm go${GO_VERSION}.linux-amd64.tar.gz
ENV PATH="/usr/local/go/bin:${PATH}"

# 4. Switch to non-root user for safe dev
USER vscode
WORKDIR /workspace

# 5. Rust (nightly, eBPF toolchain)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
    && . "/home/vscode/.cargo/env" \
    && rustup toolchain install nightly \
    && rustup component add rust-src --toolchain nightly \
    && cargo install bpf-linker cargo-generate
ENV PATH="/home/vscode/.cargo/bin:${PATH}"

# 6. Python venv & all requirements (edit as needed for poetry or pip)
COPY --chown=vscode:vscode pyproject.toml ./
# COPY --chown=vscode:vscode requirements.txt ./  
RUN python3 -m venv .venv \
    && . .venv/bin/activate \
    && pip install --upgrade pip \
    && pip install --default-timeout=600 -e ".[dev]"

# 7. Copy all sources (after venv, to avoid cache bust)
COPY --chown=vscode:vscode . .
