from machine import Pin, I2C
from lcd_i2c import LCD
import time

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=100000)
lcd = LCD(i2c, addr=0x27)

# Custom chars: plane and arrow
lcd.cmd(0x40)
for b in [0x00,0x04,0x06,0x1F,0x1F,0x06,0x04,0x00]:
    lcd.write_char(b)
lcd.cmd(0x40 + 8)
for b in [0x00,0x04,0x06,0x1F,0x06,0x04,0x00,0x00]:
    lcd.write_char(b)

msgs = [
    (chr(0) + ' IndiGo 6E2024', ' DEL ' + chr(1) + ' BLR    '),
    (chr(0) + ' IndiGo 6E2024', ' Gate 24  T1    '),
    (chr(0) + ' IndiGo 6E2024', ' Boarding Soon  '),
    (chr(0) + ' IndiGo 6E2024', '   On Time ' + chr(0) + '    '),
    ('  Welcome to   ', ' IndiGo Airlines'),
    (' Have a safe   ', '  ' + chr(0) + ' flight! ' + chr(0) + '  '),
]

while True:
    # Logo splash
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr(chr(0) + '  IndiGo  ' + chr(0))
    lcd.move_to(0, 1)
    lcd.putstr('  6E Airlines   ')
    time.sleep(3)

    # Scrolling flight info
    banner = '      IndiGo 6E2024  Delhi (DEL) ' + chr(1) + ' Bangalore (BLR)  Gate 24  T1  Boarding Soon      '
    lcd.move_to(0, 0)
    lcd.putstr(chr(0) + ' IndiGo 6E2024')
    for i in range(len(banner) - 15):
        lcd.move_to(0, 1)
        lcd.putstr(banner[i:i+16])
        time.sleep_ms(120)

    time.sleep(1)

    # Cycle static messages
    for line1, line2 in msgs:
        lcd.show(line1, line2)
        time.sleep(2)
