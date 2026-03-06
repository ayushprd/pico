from machine import Pin, I2C, ADC
from lcd_i2c import LCD
import time, random

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=100000)
lcd = LCD(i2c, addr=0x27)


def demo_clock():
    """Clock/timer with milliseconds"""
    lcd.show('  Clock Demo', '')
    time.sleep(1)
    start = time.ticks_ms()
    for i in range(50):
        elapsed = time.ticks_diff(time.ticks_ms(), start)
        secs = elapsed // 1000
        mins = secs // 60
        secs = secs % 60
        lcd.move_to(0, 0)
        lcd.putstr(f'  Timer: {mins:02d}:{secs:02d}  ')
        lcd.move_to(0, 1)
        lcd.putstr(f'   ms: {elapsed:06d}   ')
        time.sleep_ms(200)


def demo_temp():
    """CPU temperature monitor"""
    sensor = ADC(4)
    lcd.show(' CPU Temp Demo', '')
    time.sleep(1)
    for i in range(20):
        reading = sensor.read_u16()
        voltage = reading * 3.3 / 65535
        temp_c = 27 - (voltage - 0.706) / 0.001721
        temp_f = temp_c * 9/5 + 32
        lcd.move_to(0, 0)
        lcd.putstr(f'Temp: {temp_c:.1f} C    ')
        lcd.move_to(0, 1)
        lcd.putstr(f'     {temp_f:.1f} F    ')
        time.sleep_ms(500)


def demo_pomodoro():
    """Pomodoro timer (sped up demo)"""
    lcd.show(' Pomodoro Timer', '  WORK: 25:00')
    time.sleep(2)
    for secs in range(10, 0, -1):
        mins = secs // 60
        s = secs % 60
        bar = '#' * (10 - secs) + '.' * secs
        lcd.move_to(0, 0)
        lcd.putstr(f'WORK  {mins:02d}:{s:02d}     ')
        lcd.move_to(0, 1)
        lcd.putstr(f'[{bar}]     ')
        time.sleep_ms(300)
    lcd.show('  BREAK TIME!', '   5:00 left')
    time.sleep(2)


def demo_scroll():
    """Scrolling marquee text"""
    msg = '    Hello Ayush! Welcome to Raspberry Pi Pico!    '
    lcd.move_to(0, 0)
    lcd.putstr(' Scrolling Text ')
    for i in range(len(msg) - 15):
        lcd.move_to(0, 1)
        lcd.putstr(msg[i:i+16])
        time.sleep_ms(150)


def demo_custom_chars():
    """Custom characters - heart, smiley, note, lock, skull, arrow, bell, star"""
    heart = [0x00,0x0A,0x1F,0x1F,0x0E,0x04,0x00,0x00]
    smiley = [0x00,0x0A,0x0A,0x00,0x11,0x0E,0x00,0x00]
    note = [0x01,0x03,0x05,0x09,0x09,0x0B,0x1B,0x18]
    lock = [0x0E,0x11,0x11,0x1F,0x1B,0x1B,0x1F,0x00]
    skull = [0x0E,0x1F,0x15,0x1F,0x0E,0x0A,0x0A,0x00]
    arrow_r = [0x00,0x04,0x02,0x1F,0x02,0x04,0x00,0x00]
    bell = [0x04,0x0E,0x0E,0x0E,0x1F,0x00,0x04,0x00]
    star = [0x04,0x04,0x1F,0x0E,0x0E,0x15,0x04,0x00]

    chars = [heart, smiley, note, lock, skull, arrow_r, bell, star]
    for i, c in enumerate(chars):
        lcd.cmd(0x40 + i * 8)
        for b in c:
            lcd.write_char(b)

    lcd.move_to(0, 0)
    lcd.putstr('Custom Chars:   ')
    lcd.move_to(0, 1)
    for i in range(8):
        lcd.write_char(i)
        lcd.write_char(32)
    time.sleep(3)


def demo_loading():
    """Loading bar and bouncing text animation"""
    lcd.move_to(0, 0)
    lcd.putstr('  Loading...    ')
    for i in range(17):
        lcd.move_to(0, 1)
        bar = chr(0xFF) * i + '.' * (16 - i)
        lcd.putstr(bar)
        time.sleep_ms(150)
    lcd.show('  Loading...', '   COMPLETE!    ')
    time.sleep(1)

    # Bouncing text
    lcd.clear()
    msg = 'PICO'
    for pos in list(range(0, 12)) + list(range(12, 0, -1)):
        lcd.move_to(0, 0)
        lcd.putstr(' ' * 16)
        lcd.move_to(pos, 0)
        lcd.putstr(msg)
        lcd.move_to(0, 1)
        lcd.putstr(' ' * 16)
        time.sleep_ms(100)


def demo_quotes():
    """Random programming quotes"""
    quotes = [
        ('Stay hungry,', 'stay foolish.'),
        ('Keep it simple', 'stupid.'),
        ('Code is poetry.', '  - WordPress'),
        ('Talk is cheap.', 'Show me code.'),
        ('Hello, World!', '  - Every dev'),
        ('It works on my', 'machine! :)'),
        ('99 little bugs', 'in the code...'),
        ('Fix one bug,', '127 more appear'),
    ]
    random.seed(time.ticks_us())
    for _ in range(5):
        q = random.choice(quotes)
        lcd.show(q[0], q[1])
        time.sleep(2)


def run_all():
    """Run all demos"""
    demos = [demo_clock, demo_temp, demo_pomodoro, demo_scroll,
             demo_custom_chars, demo_loading, demo_quotes]
    for d in demos:
        d()
        time.sleep(1)
    lcd.show('  All demos', '  complete!')
