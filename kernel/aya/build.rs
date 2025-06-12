use std::env;
use std::path::PathBuf;
use std::process::Command;

fn main() {
    let out_dir = env::var_os("OUT_DIR").unwrap();
    let out_dir = PathBuf::from(out_dir);

    let target = if cfg!(target_arch = "aarch64") {
        "bpfel-unknown-none"
    } else {
        "bpfel-unknown-none"
    };

    println!("cargo:rerun-if-changed=lock-ebpf/src/main.rs");
    println!("cargo:rerun-if-changed=lock-common/src/lib.rs");

    let status = Command::new("cargo")
        .current_dir("lock-ebpf")
        .args(&[
            "build",
            "--target",
            target,
            "-Z",
            "build-std=core",
            "--release",
        ])
        .status()
        .expect("failed to build eBPF program");

    assert!(status.success());
} 