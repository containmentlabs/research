use aya::{
    include_bytes_aligned,
    maps::{HashMap, perf::AsyncPerfEventArray},
    programs::{Xdp, XdpFlags, KProbe},
    util::online_cpus,
    Ebpf,
};
use aya_log::EbpfLogger;
use bytes::BytesMut;
use clap::Parser;
use log::{info, warn};
use tokio::{signal, task};
use lock_common::BlockEvent;

#[derive(Debug, Parser)]
struct Opt {
    #[clap(short, long, default_value = "eth0")]
    iface: String,
    #[clap(short, long)]
    enable_network_block: bool,
    #[clap(short, long)]
    enable_syscall_block: bool,
}

#[tokio::main]
async fn main() -> Result<(), anyhow::Error> {
    let opt = Opt::parse();
    
    env_logger::init();

    #[cfg(debug_assertions)]
    let mut bpf = Ebpf::load(include_bytes_aligned!(
        "../../target/bpfel-unknown-none/debug/lock"
    ))?;
    #[cfg(not(debug_assertions))]
    let mut bpf = Ebpf::load(include_bytes_aligned!(
        "../../target/bpfel-unknown-none/release/lock"
    ))?;

    if let Err(e) = EbpfLogger::init(&mut bpf) {
        warn!("failed to initialize eBPF logger: {}", e);
    }

    let mut blocked_count: HashMap<_, u32, u32> = HashMap::try_from(bpf.map_mut("BLOCKED_SYSCALLS").unwrap())?;
    blocked_count.insert(42, 0, 0)?;
    blocked_count.insert(56, 0, 0)?;

    if opt.enable_syscall_block {
        let program: &mut KProbe = bpf.program_mut("lock_connect").unwrap().try_into()?;
        program.load()?;
        program.attach("sys_connect", 0)?;
        info!("Attached kprobe to sys_connect");

        let program: &mut KProbe = bpf.program_mut("lock_clone").unwrap().try_into()?;
        program.load()?;
        program.attach("sys_clone", 0)?;
        info!("Attached kprobe to sys_clone");
    }

    if opt.enable_network_block {
        let program: &mut Xdp = bpf.program_mut("lock_xdp").unwrap().try_into()?;
        program.load()?;
        program.attach(&opt.iface, XdpFlags::default())?;
        info!("Attached XDP to {}", opt.iface);
    }

    let mut perf_array = AsyncPerfEventArray::try_from(bpf.map_mut("EVENTS").unwrap())?;

    for cpu_id in online_cpus()? {
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
                    
                    info!(
                        "blocked syscall {} from pid {} uid {} at {}",
                        data.syscall, data.pid, data.uid, data.timestamp
                    );
                }
            }
        });
    }

    info!("L.O.C.K. kernel started. Press Ctrl-C to exit.");
    signal::ctrl_c().await?;
    info!("Exiting...");

    Ok(())
} 