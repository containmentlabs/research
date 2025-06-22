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
    
    unsafe {
        EVENTS.output(&ctx, &event, 0);
        
        let counter = BLOCKED_SYSCALLS.get_ptr_mut(&42).ok_or(0u32)?;
        *counter += 1;
    }
    
    info!(&ctx, "blocked connect() from pid={} uid={}", pid, uid);
    
    Ok(1)
}

#[kprobe]
pub fn lock_clone(ctx: ProbeContext) -> u32 {
    match try_lock_clone(ctx) {
        Ok(ret) => ret,
        Err(_) => 0,
    }
}

fn try_lock_clone(ctx: ProbeContext) -> Result<u32, u32> {
    let pid = ctx.pid();
    let uid = ctx.uid();
    
    let event = BlockEvent {
        pid,
        uid,
        syscall: 56,
        timestamp: unsafe { bpf_ktime_get_ns() },
    };
    
    unsafe {
        EVENTS.output(&ctx, &event, 0);
        
        let counter = BLOCKED_SYSCALLS.get_ptr_mut(&56).ok_or(0u32)?;
        *counter += 1;
    }
    
    info!(&ctx, "blocked clone() from pid={} uid={}", pid, uid);
    
    Ok(1)
}

#[xdp]
pub fn lock_xdp(ctx: XdpContext) -> u32 {
    match try_lock_xdp(ctx) {
        Ok(ret) => ret,
        Err(_) => xdp_action::XDP_PASS,
    }
}

fn try_lock_xdp(_ctx: XdpContext) -> Result<u32, u32> {
    Ok(xdp_action::XDP_DROP)
}

#[panic_handler]
fn panic(_info: &core::panic::PanicInfo) -> ! {
    unsafe { core::hint::unreachable_unchecked() }
} 