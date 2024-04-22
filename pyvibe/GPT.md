Groq llama3 python embedded writer

System:

You're an expert python and embedded programmer. Be a good code generation assistant. Generate code snippets like a class or a function or snippets of a function at a time for the requirement.

User (For AS5600):

use python smbus2, create a as5600 magnet encoder wrapper class: "class AS5600(object)".
It has an __init__ that takes a SMBus
It has a constant, DEV_ADDR = 0x36
It has two functions:
1. init() which sets up the chip, which is to set the hysterisis to 3 LSB, which is: set reg 0x07 = 0x0c
2. read() which returns the angle data, which is to read 2 bytes from 0x0E, low byte first, scale the 0-4096 raw value to 360 float value and return

User (For DRV2605):

use python smbus2, create a drv2605 wrapper class: "class DRV2605(object)".
It has an __init__ that takes an SMBus, and a 5 byte array of calibrated data.
It has a constant DEV_ADDR = 0x5A
It has the following functions:
0. _read_byte, _write_byte, _write_block_data that wraps the corresponding smbus methods with DEV_ADDR
1. init() which executes the following sequences in the format (register = value)
   a. 0x01 = 0x80 // reset device
   b. write the calibrated data to 0x16 - 0x1a, use __write_block_data
2. play_rtp(amp): // amp ranges from [0, 256)
   a. 0x01 = 0x45 // rtp standby
   b. 0x1d = read(0x1d) | 0x08 // toggle unsigned rtp data format
   c. 0x02 = amp // set the amplitude
   d. 0x01 = 0x05 // go
3. play_lib():
   a. 0x01 = 0x00 // internal trigger mode
   b. 0x03 = 0x06 // lib 6
   c. 0x04 = 0x18 // effect 24 in lib 6
   d. 0x0c = 0x01 // go
4. standby():
   a. 0x01 = read(0x01) | 0x40 // toggle standby

User:
extract the interface in python typing format

Assistant:
# drv2605.py
from typing import List

class DRV2605:
    def __init__(self, smbus: smbus2.SMBus, calibrated_data: List[int]) -> None
    def _read_byte(self, register: int) -> int
    def _write_byte(self, register: int, value: int) -> None
    def _write_block_data(self, register: int, data: List[int]) -> None
    def init(self) -> None
    def play_rtp(self, amp: int) -> None
    def play_lib(self) -> None
    def standby(self) -> None
# as5600.py
from typing import Self

class AS5600:
    DEV_ADDR: int

    def __init__(self, smbus: smbus2.SMBus) -> None: ...
    def init(self) -> None: ...
    def read(self) -> float: ...

User (for main.py):

With the context:
"""
# drv2605.py
from typing import List

class DRV2605:
    def __init__(self, smbus: smbus2.SMBus, calibrated_data: List[int]) -> None
    def _read_byte(self, register: int) -> int
    def _write_byte(self, register: int, value: int) -> None
    def _write_block_data(self, register: int, data: List[int]) -> None
    def init(self) -> None
    def play_rtp(self, amp: int) -> None
    def play_lib(self) -> None
    def standby(self) -> None
# as5600.py
from typing import Self

class AS5600:
    DEV_ADDR: int

    def __init__(self, smbus: smbus2.SMBus) -> None: ...
    def init(self) -> None: ...
    def read(self) -> float: ...
"""

Create an asyncio main.py that:
0. use smbus /dev/i2c-1, initialize the two sensors, particularly, the drv2605 with calibrated data: 3e 88 1e c0 aa
1. polling as5600 every 10ms, read it's angle and divide the 360deg range into 36 ticks, calc the tick based on the read angle
2. if the tick changes compared to the previous read, trigger a vibrate
3. vibrate is async, it acquires a mutex lock (to exclusively own the play status), play_rtp(128) for 5ms, release the lock, if lock fails, simply exit
