from machine import Pin, PWM
import time

MODES = {
    1: "Strobe",
    2: "Very fast strobe",
    3: "Off",
    4: "Rotating",
    5: "Rotating slow",
}

signal = PWM(Pin(3))
signal.freq(50)

def _toggle():
    signal.duty_u16(int(2000 * 65535 / 20000))
    time.sleep(0.3)
    signal.duty_u16(int(1000 * 65535 / 20000))
    time.sleep(0.3)

def next_mode():
    _toggle()

# Call next_mode() to cycle to the next mode
next_mode()
