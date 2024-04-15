## 2024-04-16

Tried to run a zephyr `native_sim_64` build. So I can use my raspberry pi's BLE and I2C for quick prototyping.

To achieve this, I choose to setup a arm64 container on mac with zephyr required tools installed and use west to build.

The result is:
1. a docker image: [Dockerfile](./docker/builder/Dockerfile)
2. a docker run cmd: [build.sh](./build.sh)

A few catchs:

The west command is `west build -b native_sim_64`.

It's not a cross-compiling so far, so I didn't install the zephyr sdk and toolchains, and instructs zephyr to use host gcc with env: `ZEPHYR_TOOLCHAIN_VARIANT=host`.

The result binary is `build/zephyr/zephyr.exe`.

On raspberry pi (with bt module), run `./zephyr.exe -bt-dev=hci0`
