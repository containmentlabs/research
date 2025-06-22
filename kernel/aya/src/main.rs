// In kernel/aya/src/main.rs

use aya::programs::KProbe;
use aya::{include_bytes_aligned, Ebpf};
use aya_log::EbpfLogger;
use log::{info, warn};
use tokio::signal;

#[tokio::main]
async fn main() -> Result<(), anyhow::Error> {
    // This will include your compiled eBPF object file
    #[cfg(debug_assertions)]
    let mut bpf = Ebpf::load(include_bytes_aligned!(
        "../../target/bpfel-unknown-none/debug/lock"
    ))?;
    #[cfg(not(debug_assertions))]
    let mut bpf = Ebpf::load(include_bytes_aligned!(
        "../../target/bpfel-unknown-none/release/lock"
    ))?;

    // This is the critical step to enable logging.
    // It finds the map named "AYA_LOGS" and starts polling it for records.
    if let Err(e) = EbpfLogger::init(&mut bpf) {
        warn!("Failed to initialize eBPF logger: {}", e);
    }

    // Attach the kprobe to the clone system call
    let clone_prog: &mut KProbe = bpf.program_mut("lock_clone").unwrap().try_into()?;
    clone_prog.load()?;
    // Note: the kernel function name may differ based on kernel version
    clone_prog.attach("__x64_sys_clone", 0)?;

    // Attach the kprobe to the connect system call
    let connect_prog: &mut KProbe = bpf.program_mut("lock_connect").unwrap().try_into()?;
    connect_prog.load()?;
    // Note: the kernel function name may differ based on kernel version
    connect_prog.attach("__x64_sys_connect", 0)?;

    info!("Waiting for Ctrl-C...");
    signal::ctrl_c().await?;
    info!("Exiting...");

    Ok(())
}