import smbus2

class DRV2605(object):
    DEV_ADDR = 0x5A

    def __init__(self, i2c, cal_data):
        self.i2c = i2c
        self.cal_data = cal_data

    def _read_byte(self, reg):
        return self.i2c.read_byte_data(self.DEV_ADDR, reg)

    def _write_byte(self, reg, value):
        self.i2c.write_byte_data(self.DEV_ADDR, reg, value)

    def _write_block_data(self, reg, values):
        self.i2c.write_block_data(self.DEV_ADDR, reg, values)

    def init(self):
        self._write_byte(0x01, 0x80)  # reset device
        # self._write_block_data(0x16, self.cal_data)
        for i in range(len(self.cal_data)):
            self._write_byte(0x16+i, self.cal_data[i])
        self.mode_lib()

    def mode_rtp(self, amp):
        self._write_byte(0x01, 0x45)  # rtp standby
        self._write_byte(0x1d, self._read_byte(0x1d) | 0x08)  # unsigned rtp data format
        self._write_byte(0x02, amp)  # set amplitude

    def play_rtp(self, amp):
        self._write_byte(0x01, 0x05)  # go

    def standby(self):
        self._write_byte(0x01, self._read_byte(0x01) | 0x40)  # standby

    def mode_lib(self):
        self._write_byte(0x01, 0x00)  # internal trigger mode
        self._write_byte(0x1d, self._read_byte(0x1d) & 0xf7)  # signed rtp data format
        self._write_byte(0x03, 0x06)  # lib 6
        self._write_byte(0x04, 0x18)  # effect 24 in lib 6

    def play_lib(self):
        self._write_byte(0x0c, 0x01)  # go
