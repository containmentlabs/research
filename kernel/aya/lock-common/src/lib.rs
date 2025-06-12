#![no_std]

#[repr(C)]
#[derive(Clone, Copy)]
pub struct BlockEvent {
    pub pid: u32,
    pub uid: u32,
    pub syscall: u32,
    pub timestamp: u64,
}

#[cfg(feature = "user")]
unsafe impl aya::Pod for BlockEvent {} 