use anyhow::anyhow;
use aya::{
    include_bytes_aligned,
    maps::perf::AsyncPerfEventArray,
    programs::KProbe,
    util::online_cpus,
    Bpf,
};
use aya_log::EbpfLogger;
use bytes::BytesMut;
use clap::Parser;
use log::{info, warn};
use lock_common::BlockEvent;
use std::net::{SocketAddr, UdpSocket};
use tokio::{signal, task};

#[derive(Debug, Parser)]
struct Opt;

#[tokio::main]
async fn main() -> Result<(), anyhow::Error> {
    let _opt = Opt::parse();

    env_logger::init();

    // This will load the eBPF program ELF file.
    let mut bpf = Bpf::load(include_bytes_aligned!(
        "../target/bpfel-unknown-none/release/lock"
    ))?;

    if let Err(e) = EbpfLogger::init(&mut bpf) {
        warn!("failed to initialize eBPF logger: {}", e);
    }

    let connect_probe: &mut KProbe = bpf.program_mut("lock_connect").unwrap().try_into()?;
    connect_probe.load()?;
    connect_probe.attach("__x64_sys_connect", 0)?;

    // The following programs are commented out because they do not exist in the current
    // eBPF code (lock-ebpf/src/main.rs). Trying to load them would cause a panic.
    // let clone_probe: &mut KProbe = bpf.program_mut("lock_clone").unwrap().try_into()?;
    // clone_probe.load()?;
    // clone_probe.attach("kernel_clone", 0)?;
    //
    // let xdp_probe: &mut Xdp = bpf.program_mut("lock_xdp").unwrap().try_into()?;
    // xdp_probe.load()?;
    // let _ = xdp_probe.attach("lo", XdpFlags::default());

    let mut perf_array = AsyncPerfEventArray::try_from(
        bpf.take_map("EVENTS")
            .ok_or(anyhow!("EVENTS map not found"))?,
    )?;

    for cpu_id in online_cpus().map_err(|e| anyhow::anyhow!("{:?}", e))? {
        let mut buf = perf_array.open(cpu_id, None)?;

        task::spawn(async move {
            let mut buffers = (0..10)
                .map(|_| BytesMut::with_capacity(1024))
                .collect::<Vec<_>>();

            loop {
                let events = buf.read_events(&mut buffers).await.unwrap();
                for i in 0..events.read {
                    let buf = &mut buffers[i];
                    let ptr = buf.as_ptr() as *const BlockEvent;
                    let data = unsafe { ptr.read_unaligned() };
                    info!("{:?}", data);
                }
            }
        });
    }

    info!("Waiting for Ctrl-C...");

    let server_addr: SocketAddr = "127.0.0.1:8080".parse().unwrap();
    let client_addr: SocketAddr = "127.0.0.1:8081".parse().unwrap();
    let socket = UdpSocket::bind(server_addr)?;
    let _ = socket.send_to(b"hello", client_addr);

    signal::ctrl_c().await.expect("failed to listen for event");
    info!("Exiting...");

    Ok(())
}
