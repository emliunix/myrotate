use std::{convert::Infallible, pin::Pin, time::Duration};

use clap::Parser;
use axum::{response::{sse::{Event, KeepAlive}, Sse}, routing::get, Router};
use i2c_linux::I2c;
use serde::Serialize;
use thiserror::Error;
use tokio::net::TcpListener;
use tokio_stream::{Stream, StreamExt};

const SENSOR_ADDR: u16 = 0x36;
const CONF_REG: u8 = 0x07;
const ANGLE_REG: u8 = 0x0E;

#[derive(Debug, Parser)]
struct AppArgs {
    #[clap(long, default_value = "/dev/i2c-1")]
    i2c_bus: String,
    #[clap(long, default_value = "0.0.0.0:8080")]
    bind_addr: String,
}

#[derive(Debug, Error)]
enum AppError {
    #[error("I2C error: {0}")]
    IoError(#[from] std::io::Error),
    #[error("Json error: {0}")]
    JsonError(#[from] serde_json::Error),
    #[error("Axum error: {0}")]
    AxumError(#[from] axum::Error),
}

#[derive(Debug, Serialize)]
struct RotaryData {
    angle: f32,
}

fn rotary_angles() -> Result<impl Stream<Item=Result<Event, Infallible>>, AppError> {
    tracing::info!("Reading rotary angle data");
    let mut bus = I2c::from_path("/dev/i2c-1")?;
    let mut last_res: Option<u16> = None;
    bus.smbus_set_slave_address(SENSOR_ADDR, false)?;
    // 3 LSBs hysteresis mode
    bus.smbus_write_byte_data(CONF_REG, 0x0c)?;
    let res = tokio_stream::iter(0..)
        .throttle(Duration::from_millis(10))
        .map(move |i| -> Result::<Option<(usize, f32)>, AppError> {
            let mut res = bus.smbus_read_word_data(ANGLE_REG)?;
            res = res << 8 | res >> 8;
            tracing::trace!("Sensor data: {:?}", res);
            if let Some(last_angle) = last_res {
                if res == last_angle {
                    return Ok(None);
                }
            }
            last_res = Some(res);
            let angle = (res as f32) / (0x1000 as f32) * 360.0;
            Ok(Some((i, angle)))
        })
        .filter_map(|res| {
            match res {
                Ok(Some((i, angle))) => Some(Ok(Event::default()
                              .id(i.to_string())
                              .event("data")
                              .json_data(RotaryData { angle }).unwrap())),
                Err(e) => {
                    tracing::error!("Error reading angle: {}", e);
                    Some(Ok(Event::default().event("error").data(format!("Error reading angle: {:?}", e))))
                }
                _ => None
            }
        });
    Ok(res)
}

async fn get_data_rotary() -> Sse<impl Stream<Item=Result<Event, Infallible>> + Send> {
    let stream: Pin<Box<dyn Stream<Item=Result<Event, Infallible>> + Send>> = match rotary_angles() {
        Ok(stream) => Box::pin(stream),
        Err(e) => {
            eprintln!("Error: {}", e);
            Box::pin(tokio_stream::empty())
        }
    };
    Sse::new(stream).keep_alive(KeepAlive::default())
}

#[tokio::main]
async fn main() -> Result<(), AppError> {
    let args = AppArgs::parse();
    tracing_subscriber::fmt()
        .with_env_filter(tracing_subscriber::EnvFilter::from_default_env())
        .init();
    let app = Router::new()
        .route("/api/data/rotary", get(get_data_rotary));
    tracing::info!("Starting server");
    axum::serve(
        TcpListener::bind(args.bind_addr).await?,
        app.into_make_service()
    ).await?;
    Ok(())
}
