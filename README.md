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

## 7. Testing the Kernel

This process verifies that the eBPF program is correctly intercepting system calls.

1.  **Ensure a Clean State**: Restart the container to kill any old, running processes.
    ```bash
    docker-compose restart research-app
    ```
    *Expected output:*
    ```text
    [+] Running 1/1
     ✔ Container research-app Restarted                                                                     0.6s
    ```

2.  **Run the Loader in the Background**: The loader is the user-space program that loads the eBPF code into the kernel and listens for events. We run it as the `root` user and in the background (`-d`). *Note the corrected path to the loader binary.*
    ```bash
    docker-compose exec -d --user root research-app /workspace/kernel/aya/target/x86_64-unknown-linux-gnu/release/lock
    ```
    This command runs in the background and should not produce any output.

3.  **Trigger an eBPF Event**: In a separate terminal, run a command that will be intercepted. For example, the `curl` command will trigger the `connect` system call probe.
    ```bash
    docker-compose exec research-app curl -s https://www.google.com > /dev/null
    ```
    This command will produce no output.

4.  **Check the Log File for Output**: The loader is configured to write events to `lock.log`. Check its contents to see the captured event.
    ```bash
    docker-compose exec research-app cat /workspace/lock.log
    ```
    You should see `BlockEvent` entries, which confirms the kernel is working.

    *Example output (PID/UID values may vary):*
    ```text
    BlockEvent { comm: "curl", pid: 12345, ppid: 123, uid: 1000, addr: "142.250.191.78" }
    ```
---
