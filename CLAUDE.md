# Pico Project

## Raspberry Pi Pico Setup
- Board: Raspberry Pi Pico (original, RP2040) — NOT Pico 2 or Pico W
- Firmware: MicroPython v1.27.0
- Serial port: /dev/ttyACM0 (needs `sudo chmod a+rw /dev/ttyACM0` after each replug until user logs out/in with dialout group)
- Tool: `mpremote` for running code from PC

## RC LED Beacon Light
- Type: RC car LED rotating beacon (orange, 3-wire servo connector)
- Wiring: Red=VBUS(5V), Brown/Dark=GND, Yellow=GP3 (signal)
- Operating voltage: 4.8-6V
- Mode control: Modes are cycled by toggling the signal wire (servo-style PWM pulse between 1000us and 2000us at 50Hz)
- 5 modes (cycled by toggling signal):
  1. Strobe
  2. Very fast strobe (sharp flash)
  3. Off
  4. Rotating (fast)
  5. Rotating slow
- Button: Wire on GP13, touch to GND to cycle modes
- Boot script: main.py on Pico (runs beacon + button listener on boot)

## Notes
- BOOTSEL button cannot be reliably read from MicroPython on RP2040 (shares flash CS line, hangs system)
- GPIO can only source ~12mA at 3.3V — not enough to power beacon directly (only 1 LED lights up). Need transistor for direct LED control.
- After reflashing via BOOTSEL bootloader mode, MicroPython must be re-flashed (UF2 at /tmp/micropython-pico.uf2)
