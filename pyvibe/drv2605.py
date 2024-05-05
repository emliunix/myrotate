import math

import smbus2

# ANSI escape codes for colors
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"


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

    def play_rtp(self):
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

    def diag(self):
        """
        This method should not be called in normal oeprating modes.
        Call mode_xxx() before normal operation.
        """
        self._write_byte(0x01, 0x06)  # into diag
        self._write_byte(0x0c, 0x01)  # go
        while self._read_byte(0x0c) & 0x01:
            pass

    def p_diag(self):
        status_reg = self._read_byte(0x00)
        diag_result_colored = (
                f"{GREEN}Passed{RESET}"
                if (status_reg & 0x08) == 0 else
                f"{RED}Failed{RESET}")
        over_temp_colored = (
                f"{RED}Over-temperature condition{RESET}"
                if (status_reg & 0x02) else
                f"{GREEN}Normal temperature{RESET}")
        over_current_colored = (
                f"{RED}Overcurrent detected{RESET}"
                if (status_reg & 0x01) else
                f"{GREEN}No overcurrent{RESET}")
        print(f"{diag_result_colored} / {over_temp_colored} / {over_current_colored}")


    @staticmethod
    def mk_lra_config(fb_brake_factor=2, init_freq=200, sample_time=3, rms_volt=0.5, overdrive_volt=0.8, blanking_time=1, idiss_time=1):
        """
        init_freq should be in [136, 1000]
        """
        drive_time = int((1000 / init_freq - 0.5) * 5)
        drive_time = max(0, min(32, drive_time))
        freq = 1000 / ((drive_time * 0.1 + 0.5) * 2)
        print(f"actual drive_time = {drive_time}, freq = {freq:.2f}")
        rv = int(round(rms_volt * math.sqrt(1 - freq * (4 * 300 + 300) / 1000_000) * 1000 / 20.58))
        ov = int(round(overdrive_volt * 1000 / 21.22))
        reg_0x16 = rv
        reg_0x17 = ov
        # feedback control (en_lra)
        reg_0x1a = 1 << 7 | fb_brake_factor << 4 | 2 << 2 | 0
        # control1 (drive_time)
        reg_0x1b = 0x93 & 0xe0 | (drive_time & 0x1f)
        reg_0x1c = 0xf5 & ((blanking_time & 0x03 << 2 + idiss_time & 0x03 << 2) | 0xf0)
        reg_0x1f = 0x80 & ((blanking_time & 0x0c << 2 + idiss_time & 0x0c << 2) | 0xf0)
        return [reg_0x16, reg_0x17, reg_0x1a, reg_0x1b, reg_0x1c, reg_0x1f]
    
    @staticmethod
    def explain(regs):
        r16, r17, r18, r19, r1a, r1b, r21, r22 = regs[:8]
        drive_time = (r1b & 0x1f) * 0.1 + 0.5
        freq = 1000 / (drive_time * 2)
        print(f"Drive Time = {drive_time:.2f}ms, freq = {freq:.2f}Hz")
        print(f"VBat = {r21 * 5.6 / 255:.2f}v")
        print(f"LRA Period = {r22 * 98.46:.2f}us")
        print(f"Rated Voltage = {r16 * 20.58 / 1000 / math.sqrt(1 - freq * (4 * 300 + 300) / 1000_000):.2f}v")
        print(f"Overdrive Clamp = {r17 * 21.22 / 1000:.2f}v")

    def calibrate(self, lra_config):
        [reg_0x16, reg_0x17, reg_0x1a, reg_0x1b, reg_0x1c, reg_0x1f] = lra_config
        self._write_byte(0x01, 0x80)  # reset
        self.p_diag()
        self._write_byte(0x16, reg_0x16)
        self._write_byte(0x17, reg_0x17)
        self._write_byte(0x1a, reg_0x1a)
        self._write_byte(0x1b, reg_0x1b)
        self._write_byte(0x1c, reg_0x1c)
        self._write_byte(0x1e, 0xf0)
        self._write_byte(0x1f, reg_0x1f)
        self._write_byte(0x01, 0x07)
        self._write_byte(0x0c, 0x01)  # go
        while self._read_byte(0x0c) & 0x01:
            pass
        self.p_diag()
        return [
            self._read_byte(0x16),
            self._read_byte(0x17),
            self._read_byte(0x18),
            self._read_byte(0x19),
            self._read_byte(0x1a),
            self._read_byte(0x1b),
            self._read_byte(0x21),
            self._read_byte(0x22),
        ]
