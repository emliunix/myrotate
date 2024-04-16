## 2024-04-17

Copied zephyr bluetooth_hids code sample for a test and failed.

```shell
*** Booting nRF Connect SDK v3.5.99-ncs1 ***
[00:00:00.000,000] <inf> my_rotate: Hello World!
[00:00:00.000,000] <inf> fs_nvs: 4 Sectors of 4096 bytes
[00:00:00.000,000] <inf> fs_nvs: alloc wra: 0, fe8
[00:00:00.000,000] <inf> fs_nvs: data wra: 0, 0
[00:00:00.000,000] <err> bt_hci_core: HCI driver open failed (-1)
[00:00:00.000,000] <err> my_rotate: Bluetooth init failed (err -1)
```

After a bit thought, I think it's better to get parts involved understood. A bit search found a rust lib `bluer` that wraps bluez.

Let's get the GATT services up and running.

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
