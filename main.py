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

button = Pin(13, Pin.IN, Pin.PULL_UP)

def _toggle():
    signal.duty_u16(int(2000 * 65535 / 20000))
    time.sleep(0.3)
    signal.duty_u16(int(1000 * 65535 / 20000))
    time.sleep(0.3)

mode = 1
print("Beacon ready - touch GP13 to GND to change mode")

while True:
    if button.value() == 0:
        _toggle()
        mode = (mode % 5) + 1
        print(f"Mode {mode}: {MODES[mode]}")
        # Wait for release
        while button.value() == 0:
            time.sleep_ms(50)
        time.sleep_ms(200)
    time.sleep_ms(50)
