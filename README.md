# Quick Start: Building & Running the Research Kernel

This guide provides the steps to get the development environment up and running for this project.

## 1. Requirements

-   Docker (latest version recommended)
-   VS Code with the "Dev Containers" extension

## 2. One-Click Setup (Recommended)

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/containmentlabs/research
    cd research
    ```

2.  **Open in VS Code & Reopen in Container**:
    -   Open the cloned folder in VS Code.
    -   If a notification appears in the bottom-right, click **"Reopen in Container"**.
    -   Alternatively, press `Ctrl+Shift+P`, type `Remote-Containers: Reopen in Container`, and press Enter.

3.  **Wait for the build to finish**.
    -   This will set up Rust (with nightly & bpfel-unknown-none), Go, Python, and all other dependencies inside a Docker container.
    -   The first build can take a while.

4.  **Verify the Build**:
    -   Once the container is running, open the VS Code terminal (it should be connected to the container).
    -   Manually run the kernel build script to ensure all binaries are compiled:
        ```bash
        bash ./scripts/build-kernel.sh
        ```

## 3. Manual Steps (If Needed)

If VS Code hangs on "Opening Remote," or if you prefer to build outside the editor:

1.  **Build & start the container**:
    ```bash
    docker-compose up -d --build
    ```

2.  **Attach to the running container**:
    -   **In VS Code**: Press `Ctrl+Shift+P` → `Remote-Containers: Attach to Running Container...` and select the `research-app` container.
    -   **In your terminal**: `docker-compose exec research-app bash`

## 4. Manual Build Steps (Inside the Container)

Once you are inside the container's shell:

1.  **Activate Python venv** (usually automatic):
    ```bash
    source .venv/bin/activate
    ```

2.  **Build the kernel**:
    ```bash
    bash ./scripts/build-kernel.sh
    ```
    (This compiles the Rust eBPF kernel and loader, plus the Go loader.)

## 5. Troubleshooting

-   If you see errors about a missing `.venv`, run:
    ```bash
    python3 -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"
    ```

-   If you hit Rust target errors, ensure the eBPF target is installed:
    ```bash
    rustup target add bpfel-unknown-none --toolchain nightly
    ```

## 6. FAQ

-   **Why passwordless sudo?**
    -   So the build scripts run smoothly in the development container. This should never be used in production.

-   **Why is the first build so slow?**
    -   The container compiles everything from scratch for a consistent setup. Future builds will be much faster by using cached layers.

-   **Can I develop natively on Windows/Mac?**
    -   No. You must always use the dev container to ensure a consistent Linux-based build environment.

-   **Where are the compiled binaries?**
    -   After a successful build (`bash ./scripts/build-kernel.sh`), you can find them here:
        -   eBPF Program: `kernel/aya/target/bpfel-unknown-none/release/lock`
        -   Rust Loader: `kernel/aya/target/release/lock`
        -   Go Loader: `kernel/loader/lock-loader`

---
