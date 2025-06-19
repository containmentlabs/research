# standard, stable version of the Microsoft dev container base image.
FROM mcr.microsoft.com/devcontainers/base:ubuntu-22.04

# set an argument for the non-root username.
ARG USERNAME=vscode

# update package lists and install all necessary dependencies
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    sudo \
    build-essential \
    libssl-dev \
    pkg-config \
    python3-dev \
    python3.10-venv \
    clang \
    llvm \
    libbpf-dev \
    linux-headers-generic \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# The base image already creates the 'vscode' user.
# The following commands will be run as this user.
USER ${USERNAME}

# Install user-specific tools: Rust and Python's 'uv'.

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/home/${USERNAME}/.cargo/bin:${PATH}"

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/home/${USERNAME}/.local/bin:${PATH}"