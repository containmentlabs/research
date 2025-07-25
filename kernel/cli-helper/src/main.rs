use anyhow::Result;
use log::info;
use lock_common::BlockEvent;

#[tokio::main]
async fn main() -> Result<()> {
    env_logger::init();
    info!("CLI Helper started. Waiting for events...");
    // Main event loop will go here
    Ok(())
} 