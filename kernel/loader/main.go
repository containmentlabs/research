package main

import (
    "log"
    "os"
    "os/signal"
    "syscall"

    "github.com/cilium/ebpf"
    "github.com/cilium/ebpf/link"
)

const bpfObjectPath = "../aya/target/bpfel-unknown-none/release/lock"

func main() {
    // Subscribe to signals for graceful shutdown
    stopper := make(chan os.Signal, 1)
    signal.Notify(stopper, os.Interrupt, syscall.SIGTERM)

    // Load the compiled eBPF ELF file into a CollectionSpec.
    spec, err := ebpf.LoadCollectionSpec(bpfObjectPath)
    if err!= nil {
        log.Fatalf("failed to load BPF collection spec: %v", err)
    }

    // Instantiate the BPF programs and maps from the spec.
    coll, err := ebpf.NewCollection(spec)
    if err!= nil {
        log.Fatalf("failed to create BPF collection: %v", err)
    }
    defer coll.Close()

    // Attach the kprobe to the clone system call
    cloneProg, ok := coll.Programs["lock_clone"]
    if!ok {
        log.Fatalf("eBPF program 'lock_clone' not found")
    }
    cloneLink, err := link.Kprobe("__x64_sys_clone", cloneProg, nil)
    if err!= nil {
        log.Fatalf("failed to attach clone kprobe: %v", err)
    }
    defer cloneLink.Close()

    // Attach the kprobe to the connect system call
    connectProg, ok := coll.Programs["lock_connect"]
    if!ok {
        log.Fatalf("eBPF program 'lock_connect' not found")
    }
    connectLink, err := link.Kprobe("__x64_sys_connect", connectProg, nil)
    if err!= nil {
        log.Fatalf("failed to attach connect kprobe: %v", err)
    }
    defer connectLink.Close()

    log.Println("Successfully loaded and attached eBPF programs. Waiting for events...")

    // Wait for a signal to exit.
    <-stopper
    log.Println("Received signal, exiting...")
}