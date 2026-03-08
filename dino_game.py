from machine import Pin, I2C
from lcd_i2c import LCD
import time, random, sys

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=100000)
lcd = LCD(i2c, addr=0x27)

# Custom characters
DINO_RUN1 = [0b00111,0b00101,0b00111,0b10110,0b11111,0b01110,0b01010,0b10001]
DINO_RUN2 = [0b00111,0b00101,0b00111,0b10110,0b11111,0b01110,0b01010,0b01001]
DINO_JUMP = [0b00111,0b00101,0b00111,0b10110,0b11111,0b01110,0b01010,0b01010]
CACTUS =    [0b00100,0b10101,0b10101,0b10110,0b01100,0b00100,0b00100,0b00100]
BIRD =      [0b00000,0b00100,0b01110,0b11111,0b00100,0b00000,0b00000,0b00000]

lcd.custom_char(0, DINO_RUN1)
lcd.custom_char(1, DINO_RUN2)
lcd.custom_char(2, DINO_JUMP)
lcd.custom_char(3, CACTUS)
lcd.custom_char(4, BIRD)

import select
poll = select.poll()
poll.register(sys.stdin, select.POLLIN)

def key_pressed():
    return poll.poll(0)

def drain():
    while poll.poll(0):
        sys.stdin.read(1)

def run():
    obstacles = []
    score = 0
    dino_row = 1
    jump_ticks = 0
    frame = 0
    speed = 180

    lcd.clear()
    lcd.show("  DINO RUNNER!  ", "  Press a key!  ")

    # wait for keypress to start
    drain()
    while not key_pressed():
        time.sleep_ms(50)
    drain()
    lcd.clear()
    time.sleep_ms(300)

    while True:
        if key_pressed():
            drain()
            if dino_row == 1:
                dino_row = 0
                jump_ticks = 6

        if jump_ticks > 0:
            jump_ticks -= 1
            if jump_ticks == 0:
                dino_row = 1

        if len(obstacles) == 0 or (obstacles[-1][0] < 12 and random.random() < 0.3):
            obstacles.append([15, 1] if random.random() < 0.75 else [15, 0])

        new_obs = []
        for ob in obstacles:
            ob[0] -= 1
            if ob[0] >= 0:
                new_obs.append(ob)
        obstacles = new_obs

        for ob in obstacles:
            if ob[0] == 1 and ob[1] == dino_row:
                lcd.show("  GAME  OVER!  ", f"  Score: {score:>5}  ")
                print(f"\nGame over! Score: {score}")
                print("Run: import dino_game; dino_game.run()")
                time.sleep(2)
                return score

        top = [' '] * 16
        bot = [' '] * 16

        if dino_row == 0:
            top[1] = '\x02'
        else:
            bot[1] = chr(frame % 2)

        for ob in obstacles:
            if ob[1] == 0:
                top[ob[0]] = '\x04'
            else:
                bot[ob[0]] = '\x03'

        sc_str = str(score)
        for i, c in enumerate(sc_str):
            top[15 - len(sc_str) + 1 + i] = c

        lcd.move_to(0, 0)
        lcd.putstr(''.join(top))
        lcd.move_to(0, 1)
        lcd.putstr(''.join(bot))

        score += 1
        frame += 1
        if score % 50 == 0 and speed > 80:
            speed -= 10
        time.sleep_ms(speed)

print("Type: run() then press Enter")
