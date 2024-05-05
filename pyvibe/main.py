import asyncio
import smbus2
from drv2605 import DRV2605
from as5600 import AS5600

# Initialize I2C bus
i2c_bus = smbus2.SMBus(1)  # /dev/i2c-1

# Initialize sensors
drv2605_calibrated_data = [0x3e, 0x88, 0x1e, 0xc0, 0xaa]
drv2605 = DRV2605(i2c_bus, drv2605_calibrated_data)
as5600 = AS5600(i2c_bus)

# Initialize mutex for exclusive access to DRV2605
play_mutex = asyncio.Lock()


class IntoLibMode(object):
    def __init__(self, drv2605):
        self.drv2605 = drv2605
        self.drv2605.mode_lib()

    async def play(self):
        if play_mutex.locked():
            return
        async with play_mutex:
            self.drv2605.play_lib()


class IntoRTPMode(object):
    def __init__(self, drv2605, amp):
        self.drv2605 = drv2605
        self.drv2605.diag()
        self.drv2605.p_diag()
        self.drv2605.mode_rtp(amp)

    async def play(self):
        if play_mutex.locked():
            return
        async with play_mutex:
            self.drv2605.play_rtp()
            await asyncio.sleep(0.01)
            self.drv2605.standby()


async def vibrate():
        print("vibrate")
        drv2605.play_rtp(1)
        await asyncio.sleep(0.005)  # 5ms
        drv2605.standby()

async def main():
    prev_loc = None
    # drv2605_play = IntoLibMode(drv2605)
    DRV2605.explain(drv2605.calibrate(DRV2605.mk_lra_config(init_freq=210, rms_volt=1.2, overdrive_volt=3.3, blanking_time=1, idiss_time=1)))
    drv2605_play = IntoRTPMode(drv2605, 255)
    while True:
        angle = as5600.read()
        if prev_loc is None:
            prev_loc = angle
        else:
            delta = angle - prev_loc 
            if abs(delta) > 10:
                print(f"Angle: {angle:.2f}deg, Tick: {'+' if delta > 0 else '-'}")
                asyncio.create_task(drv2605_play.play())
                prev_loc = angle
        await asyncio.sleep(0.01)  # 10ms

async def init_sensors():
    drv2605.init()
    as5600.init()

async def main_loop():
    await init_sensors()
    await main()

if __name__ == "__main__":
    asyncio.run(main_loop())
