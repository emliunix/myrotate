use bluer::gatt::local::{Characteristic, CharacteristicRead, Service};
use thiserror::Error;

#[derive(Error, Debug)]
enum AppError {
    #[error("bluer error")]
    Bluer(#[from] bluer::Error),
    #[error("io error")]
    Io(#[from] std::io::Error),
}

fn mk_battery_characteristic() -> Characteristic {
    let uuid = bluer::id::Characteristic::BatteryLevel.into();
    Characteristic {
        uuid,
        read: Some(CharacteristicRead {
            read: true,
            fun: Box::new(move |req| {
                Box::pin(async move {
                    Ok(vec![1u8])
                })
            }),
            ..Default::default()
        }),
        ..Default::default()
    }
}

fn mk_service() -> Service {
    let uuid = bluer::id::Service::BatteryService.into();
    Service {
        uuid,
        handle: None,
        primary: true,
        characteristics: vec![mk_battery_characteristic()],
        ..Default::default()
    }
}

#[tokio::main(flavor = "current_thread")]
async fn main() -> Result<(), AppError> {
    env_logger::init();
    log::info!("Starting up");
    let session = bluer::Session::new().await?;
    let adapter = session.default_adapter().await?;
    adapter.set_powered(true).await?;

    log::info!("Advertise");

    log::info!("Start app");

    Ok(())
}
