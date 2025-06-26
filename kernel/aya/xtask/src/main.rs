use clap::Parser;
use std::env;
use std::fs;
use std::process::Command as ProcessCommand;

#[derive(Debug, Parser)]
pub struct Options {
    #[clap(subcommand)]
    command: Command,
}

#[derive(Debug, Parser)]
enum Command {
    BuildEbpf(BuildEbpfOptions),
}

#[derive(Debug, Parser)]
struct BuildEbpfOptions {
    #[clap(long)]
    release: bool,
}

fn main() -> Result<(), anyhow::Error> {
    let opts = Options::parse();

    use Command::*;
    match opts.command {
        BuildEbpf(opts) => build_ebpf(opts),
    }
}

fn build_ebpf(opts: BuildEbpfOptions) -> Result<(), anyhow::Error> {
    let dir = env::current_dir()?;
    let target = "bpfel-unknown-none";

    let mut args = vec![
        "+nightly",
        "build",
        "--target",
        target,
        "-Z",
        "build-std=core,alloc",
    ];
    if opts.release {
        args.push("--release");
    }

    let status = ProcessCommand::new("cargo")
        .args(&args)
        .current_dir(dir.join("lock-ebpf"))
        .status()?;

    if !status.success() {
        anyhow::bail!("Failed to build eBPF program");
    }

    let binary_path = dir.join("target/bpfel-unknown-none/release/lock");
    let out_dir = dir.join("target/ebpf");
    fs::create_dir_all(&out_dir)?;
    let out_path = out_dir.join("lock");
    fs::copy(&binary_path, &out_path)?;

    println!("eBPF binary copied to {}", out_path.display());

    Ok(())
}
