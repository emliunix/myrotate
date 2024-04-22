import smbus2

class AS5600(object):
    DEV_ADDR = 0x36

    def __init__(self, bus):
        self.bus = bus

    def init(self):
        self.bus.write_byte_data(self.DEV_ADDR, 0x07, 0x0C)

    def read(self):
        raw_data = self.bus.read_i2c_block_data(self.DEV_ADDR, 0x0E, 2)
        angle_raw = (raw_data[0] << 8) | raw_data[1]
        angle_deg = (angle_raw / 4096.0) * 360.0
        return angle_deg
