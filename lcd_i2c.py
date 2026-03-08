from machine import I2C
import time

class LCD:
    def __init__(self, i2c, addr=0x27, cols=16, rows=2):
        self.i2c = i2c
        self.addr = addr
        self.cols = cols
        self.rows = rows
        self.backlight = 0x08
        self._write4(0x03)
        self._write4(0x03)
        self._write4(0x03)
        self._write4(0x02)
        self.cmd(0x28)  # 4-bit, 2 lines, 5x8
        self.cmd(0x0C)  # display on, cursor off
        self.cmd(0x06)  # entry mode
        self.cmd(0x01)  # clear
        time.sleep_ms(2)

    def _write_byte(self, val):
        for _ in range(3):
            try:
                self.i2c.writeto(self.addr, bytes([val]))
                return
            except OSError:
                pass

    def _pulse(self, val):
        self._write_byte(val | 0x04)
        time.sleep_us(1)
        self._write_byte(val & ~0x04)
        time.sleep_us(50)

    def _write4(self, val, mode=0):
        b = (val << 4) & 0xF0 | mode | self.backlight
        self._pulse(b)

    def _write(self, val, mode=0):
        hi = (val & 0xF0) | mode | self.backlight
        lo = ((val << 4) & 0xF0) | mode | self.backlight
        self._pulse(hi)
        self._pulse(lo)

    def cmd(self, val):
        self._write(val, 0)
        if val <= 3:
            time.sleep_ms(2)

    def write_char(self, val):
        self._write(val, 0x01)

    def clear(self):
        self.cmd(0x01)
        time.sleep_ms(2)

    def move_to(self, col, row):
        addr = col + (0x40 if row else 0x00)
        self.cmd(0x80 | addr)

    def custom_char(self, loc, charmap):
        self.cmd(0x40 | (loc << 3))
        for row in charmap:
            self.write_char(row)

    def putstr(self, s):
        for c in s:
            self.write_char(ord(c))

    def _pad(self, s):
        s = s[:self.cols]
        return s + ' ' * (self.cols - len(s))

    def show(self, line1="", line2=""):
        self.move_to(0, 0)
        self.putstr(self._pad(line1))
        self.move_to(0, 1)
        self.putstr(self._pad(line2))
