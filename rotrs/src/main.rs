#![feature(proc_macro_c_str_literals)]

use bluer::gatt::local::{Characteristic, Service};

#[thiserror::Error]
enum AppError {
    Bluer(bluer::Error),
    Io(std::io::Error),
}

fn mk_battery_characteristic() -> Characteristic {
    let mut characteristic = Characteristic::new(bluer::id::BatteryLevel::UUID);
    characteristic.set_value(vec![0x64]);
    characteristic
}

fn mk_service() -> Service {
    let uuid = Uuid::parse_str("0000180a-0000-1000-8000-00805f9b34fb").unwrap();
    Service {
        uuid,
        handle: None,
        primary: true,
        characteristics: vec![],
        control_handle: Default::default(),
        _non_exhaustive: Default::default(),
    }
}

#[tokio::main(flavor = "current_thread")]
fn main() -> Result<(), AppError> {
    env_logger::init();
    log::info!("Starting up");
    let session = bluer::Session::new().await?;
    let adapter = session.default_adapter().await?;
    adapter.set_powered(true).await?;

    log::info!("Advertise");

    log::info!("Start app");

    Ok(())
}
