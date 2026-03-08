from machine import Pin, I2C
from lcd_i2c import LCD
import time, random

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=100000)
lcd = LCD(i2c, addr=0x27)

# Custom characters for eyes and face parts
# Eye open (left)
EYE_OPEN_L = [
    0b00000,
    0b01110,
    0b11111,
    0b11011,
    0b11011,
    0b11111,
    0b01110,
    0b00000,
]
# Eye open (right) - same as left
EYE_OPEN_R = EYE_OPEN_L

# Eye half closed
EYE_HALF = [
    0b00000,
    0b00000,
    0b01110,
    0b11111,
    0b11011,
    0b11111,
    0b01110,
    0b00000,
]

# Eye closed (blink)
EYE_CLOSED = [
    0b00000,
    0b00000,
    0b00000,
    0b01110,
    0b11111,
    0b01110,
    0b00000,
    0b00000,
]

# Eye looking left
EYE_LOOK_L = [
    0b00000,
    0b01110,
    0b11111,
    0b11101,
    0b11101,
    0b11111,
    0b01110,
    0b00000,
]

# Eye looking right
EYE_LOOK_R = [
    0b00000,
    0b01110,
    0b11111,
    0b10111,
    0b10111,
    0b11111,
    0b01110,
    0b00000,
]

# Eye looking up
EYE_LOOK_UP = [
    0b00000,
    0b01110,
    0b11011,
    0b11011,
    0b11111,
    0b11111,
    0b01110,
    0b00000,
]

# Mouth happy
MOUTH_HAPPY = [
    0b00000,
    0b00000,
    0b00000,
    0b10001,
    0b10001,
    0b01110,
    0b00000,
    0b00000,
]

# Mouth sad
MOUTH_SAD = [
    0b00000,
    0b00000,
    0b00000,
    0b01110,
    0b10001,
    0b10001,
    0b00000,
    0b00000,
]

# Mouth open (surprised)
MOUTH_OPEN = [
    0b00000,
    0b00000,
    0b00000,
    0b01110,
    0b10001,
    0b01110,
    0b00000,
    0b00000,
]

# Mouth flat
MOUTH_FLAT = [
    0b00000,
    0b00000,
    0b00000,
    0b00000,
    0b11111,
    0b00000,
    0b00000,
    0b00000,
]

# Heart
HEART = [
    0b00000,
    0b01010,
    0b11111,
    0b11111,
    0b11111,
    0b01110,
    0b00100,
    0b00000,
]

def load_face(left_eye, right_eye, mouth):
    lcd.custom_char(0, left_eye)
    lcd.custom_char(1, right_eye)
    lcd.custom_char(2, mouth)

def draw_face(expr_text=""):
    lcd.move_to(5, 0)
    lcd.write_char(0)  # left eye
    lcd.putstr("    ")
    lcd.write_char(1)  # right eye
    lcd.move_to(5, 1)
    lcd.putstr("  ")
    lcd.write_char(2)  # mouth
    lcd.putstr("  ")
    if expr_text:
        lcd.move_to(0, 0)
        lcd.putstr(expr_text[:4])

def blink():
    # half close
    load_face(EYE_HALF, EYE_HALF, MOUTH_HAPPY)
    draw_face()
    time.sleep_ms(60)
    # closed
    load_face(EYE_CLOSED, EYE_CLOSED, MOUTH_HAPPY)
    draw_face()
    time.sleep_ms(100)
    # half open
    load_face(EYE_HALF, EYE_HALF, MOUTH_HAPPY)
    draw_face()
    time.sleep_ms(60)
    # open
    load_face(EYE_OPEN_L, EYE_OPEN_R, MOUTH_HAPPY)
    draw_face()

def look_around():
    load_face(EYE_LOOK_L, EYE_LOOK_L, MOUTH_FLAT)
    draw_face()
    time.sleep(0.5)
    load_face(EYE_LOOK_R, EYE_LOOK_R, MOUTH_FLAT)
    draw_face()
    time.sleep(0.5)
    load_face(EYE_OPEN_L, EYE_OPEN_R, MOUTH_HAPPY)
    draw_face()

def surprised():
    load_face(EYE_LOOK_UP, EYE_LOOK_UP, MOUTH_OPEN)
    draw_face(" !  ")
    time.sleep(1)
    load_face(EYE_OPEN_L, EYE_OPEN_R, MOUTH_HAPPY)
    draw_face("    ")

def sad_face():
    load_face(EYE_HALF, EYE_HALF, MOUTH_SAD)
    draw_face(" :(  ")
    time.sleep(1.5)
    load_face(EYE_OPEN_L, EYE_OPEN_R, MOUTH_HAPPY)
    draw_face("    ")

def love_face():
    lcd.custom_char(0, HEART)
    lcd.custom_char(1, HEART)
    lcd.custom_char(2, MOUTH_HAPPY)
    draw_face(" <3 ")
    time.sleep(1.5)
    load_face(EYE_OPEN_L, EYE_OPEN_R, MOUTH_HAPPY)
    draw_face("    ")

def wink():
    load_face(EYE_CLOSED, EYE_OPEN_R, MOUTH_HAPPY)
    draw_face(" ;) ")
    time.sleep(0.6)
    load_face(EYE_OPEN_L, EYE_OPEN_R, MOUTH_HAPPY)
    draw_face("    ")

def sleepy():
    lcd.clear()
    load_face(EYE_HALF, EYE_HALF, MOUTH_FLAT)
    draw_face(" Zzz")
    time.sleep(0.5)
    load_face(EYE_CLOSED, EYE_CLOSED, MOUTH_FLAT)
    draw_face(" Zzz")
    time.sleep(1)
    load_face(EYE_CLOSED, EYE_CLOSED, MOUTH_FLAT)
    draw_face("zZzZ")
    time.sleep(1)
    # wake up
    load_face(EYE_HALF, EYE_HALF, MOUTH_OPEN)
    draw_face(" !? ")
    time.sleep(0.5)
    load_face(EYE_OPEN_L, EYE_OPEN_R, MOUTH_HAPPY)
    draw_face("    ")

# --- Main loop ---
lcd.clear()
load_face(EYE_OPEN_L, EYE_OPEN_R, MOUTH_HAPPY)
draw_face()
print("Robot face running!")

expressions = [look_around, surprised, sad_face, love_face, wink, sleepy]

while True:
    # Random idle time with occasional blinks
    wait = random.uniform(1.5, 3.5)
    start = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start) < int(wait * 1000):
        time.sleep_ms(100)

    # Blink (common) or expression (less common)
    if random.random() < 0.6:
        blink()
        # Sometimes double blink
        if random.random() < 0.3:
            time.sleep_ms(150)
            blink()
    else:
        random.choice(expressions)()
