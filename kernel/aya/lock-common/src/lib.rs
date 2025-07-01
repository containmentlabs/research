    #![no_std]

    #[cfg(feature = "user")]
    use aya::Pod;

    #[repr(C)]
    #[derive(Clone, Copy, Debug)]
    #[cfg_attr(feature = "user", derive(Pod))]
    pub struct BlockEvent {
        pub pid: u32,
        pub uid: u32,
        pub syscall: u32,
        pub timestamp: u64,
    }
