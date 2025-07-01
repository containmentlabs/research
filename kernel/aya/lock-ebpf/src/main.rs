    #![no_std]
    #![no_main]

    use aya_ebpf::{
        bindings::xdp_action,
        macros::{kprobe, map, xdp},
        maps::{HashMap, PerfEventArray},
        programs::{ProbeContext, XdpContext},
        helpers::bpf_ktime_get_ns,
        EbpfContext
    };
    use aya_log_ebpf::info;
    use lock_common::BlockEvent;

    #[map]
    static mut EVENTS: PerfEventArray<BlockEvent> = PerfEventArray::new(0);

    #[map]
    static mut BLOCKED_SYSCALLS: HashMap<u32, u32> = HashMap::with_max_entries(1024, 0);

    #[kprobe]
    pub fn lock_connect(ctx: ProbeContext) -> u32 {
        match try_lock_connect(ctx) {
            Ok(ret) => ret,
            Err(_) => 0,
        }
    }

    fn try_lock_connect(ctx: ProbeContext) -> Result<u32, u32> {
        let pid = ctx.pid();
        let uid = ctx.uid();
        let event = BlockEvent {
            pid,
            uid,
            syscall: 42,
            timestamp: unsafe { bpf_ktime_get_ns() },
        };
        unsafe { EVENTS.output(&ctx, &event, 0) };
        info!(&ctx, "blocked connect() from pid={} uid={}", pid, uid);
        Ok(1)
    }

    #[panic_handler]
    fn panic(_info: &core::panic::PanicInfo) -> ! {
        unsafe { core::hint::unreachable_unchecked() }
    }
