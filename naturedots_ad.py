from machine import Pin, I2C
from lcd_i2c import LCD
import time, random

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=100000)
lcd = LCD(i2c, addr=0x27)

# Custom chars
drop =    [0x04,0x04,0x0E,0x0E,0x1F,0x1F,0x0E,0x00]  # 0
leaf =    [0x02,0x06,0x0E,0x1C,0x0E,0x06,0x02,0x00]  # 1
globe =   [0x0E,0x11,0x15,0x11,0x15,0x11,0x0E,0x00]  # 2
fish =    [0x00,0x04,0x0E,0x1F,0x0E,0x04,0x00,0x00]  # 3
bolt =    [0x02,0x04,0x0F,0x02,0x04,0x08,0x00,0x00]  # 4
wave =    [0x01,0x03,0x07,0x0E,0x1C,0x18,0x10,0x00]  # 5
heart_s = [0x00,0x0A,0x15,0x11,0x0A,0x04,0x00,0x00]  # 6 small
heart_l = [0x00,0x0A,0x1F,0x1F,0x0E,0x04,0x00,0x00]  # 7 big

chars = [drop, leaf, globe, fish, bolt, wave, heart_s, heart_l]
for i, c in enumerate(chars):
    lcd.cmd(0x40 + i * 8)
    for b in c:
        lcd.write_char(b)

def icon(col, row, cid):
    lcd.move_to(col, row)
    lcd.write_char(cid)

def typr(col, row, text, delay=50):
    lcd.move_to(col, row)
    for ch in text:
        lcd.write_char(ord(ch))
        time.sleep_ms(delay)

def clr():
    lcd.clear()

def water_fill():
    for col in range(16):
        lcd.move_to(col, 1)
        lcd.write_char(0xFF)
        time.sleep_ms(20)
    for col in range(16):
        lcd.move_to(col, 0)
        lcd.write_char(0xFF)
        time.sleep_ms(20)
    for col in range(16):
        lcd.move_to(col, 0)
        lcd.write_char(32)
        time.sleep_ms(20)
    for col in range(16):
        lcd.move_to(col, 1)
        lcd.write_char(32)
        time.sleep_ms(20)

def blink_heart(col, row, times=3):
    for _ in range(times):
        icon(col, row, 7)
        time.sleep_ms(300)
        icon(col, row, 6)
        time.sleep_ms(300)

random.seed(time.ticks_us())

while True:
    # SCENE 1: Rain drops
    lcd.show('', '')
    for frame in range(12):
        lcd.show('', '')
        for _ in range(4):
            icon(random.randint(0, 15), random.randint(0, 1), 0)
        time.sleep_ms(180)

    # SCENE 2: Question
    lcd.show('', '')
    icon(0, 0, 0)
    typr(1, 0, ' What if water', 45)
    typr(1, 1, ' could talk?', 45)
    icon(14, 1, 0)
    time.sleep(2.5)

    # SCENE 3: Water fill + Logo
    water_fill()
    lcd.show('', '')
    time.sleep(0.3)
    logo = 'NatureDots'
    col = 3
    for i, ch in enumerate(logo):
        lcd.move_to(col + i, 0)
        lcd.write_char(0xFF)
        time.sleep_ms(60)
        lcd.move_to(col + i, 0)
        lcd.write_char(ord(ch))
        time.sleep_ms(30)
    time.sleep(0.4)
    icon(2, 1, 0)
    typr(3, 1, ' Water AI ', 50)
    icon(14, 1, 1)
    time.sleep(2.5)

    # SCENE 4: AquaNurch
    water_fill()
    lcd.show('', '')
    icon(1, 0, 3)
    typr(2, 0, ' AquaNurch', 50)
    typr(2, 1, 'Digital Twin', 50)
    time.sleep(2.5)

    # SCENE 5: Stats
    stats = [
        (' 275,000+ Ha', ' Water Managed', 2),
        (' 630M Litres', ' Water Saved', 0),
        (' 1,300+ Users', ' Across India', 2),
        (' 95% Accuracy', ' 100x Faster', 4),
        (' 17+ Aqua', ' Eco-Zones', 3),
    ]
    for s1, s2, ic in stats:
        water_fill()
        lcd.move_to(0, 0)
        lcd.write_char(ic)
        typr(1, 0, s1, 30)
        typr(0, 1, s2, 30)
        time.sleep(2)

    # SCENE 6: Heart - We love water
    water_fill()
    lcd.show('', '')
    typr(3, 0, 'We  Water', 80)
    icon(6, 0, 7)
    typr(2, 1, 'For Everyone', 60)
    blink_heart(6, 0, 5)
    time.sleep(1)

    # SCENE 7: Mission scroll
    water_fill()
    lcd.show('', '')
    icon(0, 0, 1)
    typr(1, 0, ' Our Mission', 40)
    mission = '      Data equity is water equity. Predicting water crises before they happen.      '
    for i in range(len(mission) - 15):
        lcd.move_to(0, 1)
        lcd.putstr(mission[i:i+16])
        time.sleep_ms(130)
    time.sleep(1)

    # SCENE 8: Wave + logo
    water_fill()
    lcd.show('', '')
    for frame in range(16):
        lcd.move_to(0, 1)
        for c in range(16):
            lcd.write_char(5 if (c + frame) % 3 == 0 else 32)
        lcd.move_to(3, 0)
        lcd.putstr('NatureDots')
        time.sleep_ms(200)

    # SCENE 9: CTA with heart
    water_fill()
    lcd.show('', '')
    icon(1, 0, 2)
    typr(3, 0, 'Join Us', 60)
    icon(11, 0, 2)
    typr(1, 1, 'naturedots.com', 50)
    time.sleep(1)
    blink_heart(1, 0, 4)
    time.sleep(1)

    # SCENE 10: Closing with heartbeat
    water_fill()
    lcd.show('', '')
    typr(3, 0, 'NatureDots', 60)
    icon(0, 1, 0)
    typr(1, 1, ' Save Water ', 60)
    icon(14, 1, 7)
    blink_heart(14, 1, 5)
    time.sleep(1)

    # Fade out
    for _ in range(5):
        lcd.cmd(0x08)
        time.sleep_ms(300)
        lcd.cmd(0x0C)
        time.sleep_ms(300)
    lcd.cmd(0x08)
    time.sleep(2)
    lcd.cmd(0x0C)
