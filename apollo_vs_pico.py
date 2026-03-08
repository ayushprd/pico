from machine import Pin, I2C
from lcd_i2c import LCD
import time, random, math

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=100000)
lcd = LCD(i2c, addr=0x27)


def title(line1, line2, pause=2):
    lcd.show(line1, line2)
    time.sleep(pause)


# --- Demo 1: Pi Digits ---
def pi_digits():
    """Compute pi digits using Machin's formula with integer arithmetic"""
    title(" [1] Pi Digits", "Computing...")

    def arccot(x, n_digits):
        power = 10 ** (n_digits + 10)
        total = 0
        x_power = power // x
        n = 1
        sign = 1
        while x_power:
            total += sign * (x_power // n)
            x_power //= (x * x)
            n += 2
            sign = -sign
        return total

    t0 = time.ticks_ms()
    digits = 50
    pi_int = 4 * (4 * arccot(5, digits) - arccot(239, digits))
    pi_int //= 10 ** 10  # trim guard digits
    elapsed = time.ticks_diff(time.ticks_ms(), t0)

    pi_str = str(pi_int)
    pi_str = pi_str[0] + '.' + pi_str[1:]

    # Show timing
    lcd.show(f"  {elapsed}ms to get", f"  {digits} digits!")
    time.sleep(2)

    lcd.show("1961 IBM took 9h", "for 100K digits!")
    time.sleep(2)

    # Scroll pi digits
    lcd.show("Pi=", "")
    full = pi_str
    for i in range(len(full) - 15):
        lcd.move_to(0, 0)
        lcd.putstr(full[i:i + 16])
        lcd.move_to(0, 1)
        lcd.putstr(f"  Pico: {elapsed}ms   "[:16])
        time.sleep_ms(300)


# --- Demo 2: Prime Sieve ---
def prime_sieve():
    title(" [2] Primes", "Sieving...")

    limit = 100000
    t0 = time.ticks_ms()

    # Bit-packed sieve to save RAM
    sieve = bytearray((limit + 7) // 8)
    count = 0
    for i in range(2, limit):
        if not (sieve[i >> 3] & (1 << (i & 7))):
            count += 1
            if i * i < limit:
                for j in range(i * i, limit, i):
                    sieve[j >> 3] |= (1 << (j & 7))

    elapsed = time.ticks_diff(time.ticks_ms(), t0)

    lcd.show(f"Primes<100K:", f"  {count} in {elapsed}ms")
    time.sleep(3)
    lcd.show("ENIAC (1946):", "Would take hours!")
    time.sleep(2)


# --- Demo 3: Monte Carlo Pi ---
def monte_carlo():
    title("[3] Monte Carlo", "Estimating Pi...")
    time.sleep(1)

    inside = 0
    total = 0
    t0 = time.ticks_ms()

    for batch in range(50):
        for _ in range(200):
            x = random.random()
            y = random.random()
            if x * x + y * y <= 1.0:
                inside += 1
            total += 1

        pi_est = 4.0 * inside / total
        elapsed = time.ticks_diff(time.ticks_ms(), t0)
        lcd.show(f"Pi~{pi_est:.10f}"[:16], f"n={total} {elapsed}ms")

    time.sleep(1)
    lcd.show("1948: ENIAC ran", "this for weeks!")
    time.sleep(2)


# --- Demo 4: Trajectory ---
def trajectory():
    title("[4] Trajectory", "Artillery calc...")
    time.sleep(1)

    # Projectile with drag (what human computers spent 20hrs on)
    t0 = time.ticks_ms()

    dt = 0.01
    x, y = 0.0, 0.0
    vx, vy = 500.0, 500.0  # m/s
    g = 9.81
    drag = 0.001
    steps = 0
    max_alt = 0.0

    while y >= 0 or steps < 10:
        speed = math.sqrt(vx * vx + vy * vy)
        ax = -drag * speed * vx
        ay = -g - drag * speed * vy
        vx += ax * dt
        vy += ay * dt
        x += vx * dt
        y += vy * dt
        steps += 1
        if y > max_alt:
            max_alt = y

        if steps % 500 == 0 and y > 0:
            lcd.show(f"Alt:{y:.0f}m", f"Vel:{speed:.0f}m/s")

        if y < 0 and steps > 10:
            break

    elapsed = time.ticks_diff(time.ticks_ms(), t0)

    lcd.show(f"Range:{x:.0f}m", f"MaxAlt:{max_alt:.0f}m")
    time.sleep(2)
    lcd.show(f"Pico: {elapsed}ms", "Human: 20 hours!")
    time.sleep(2)
    lcd.show(f"{steps} steps done", "ENIAC took 30s!")
    time.sleep(2)


# --- Demo 5: Big Factorials ---
def factorials():
    title("[5] Factorials", "Big numbers...")
    time.sleep(1)

    # AGC had 15-bit words: max 16383
    lcd.show("AGC max number:", "     16,383")
    time.sleep(2)

    lcd.show("Pico computes:", "")
    time.sleep(1)

    for n in [15, 20, 25, 30]:
        t0 = time.ticks_ms()
        result = 1
        for i in range(2, n + 1):
            result *= i
        elapsed = time.ticks_diff(time.ticks_ms(), t0)

        r_str = str(result)
        lcd.show(f"{n}! ({len(r_str)} digits)", "")
        time.sleep(0.5)

        # Scroll the number
        if len(r_str) <= 16:
            lcd.move_to(0, 1)
            lcd.putstr(r_str[:16])
            time.sleep(1.5)
        else:
            for i in range(len(r_str) - 15):
                lcd.move_to(0, 1)
                lcd.putstr(r_str[i:i + 16])
                time.sleep_ms(200)

    lcd.show("AGC couldn't do", "any of this!")
    time.sleep(2)


# --- Demo 6: Matrix Nav ---
def matrix_nav():
    title("[6] Navigation", "Matrix math...")
    time.sleep(1)

    # Apollo-style coordinate transform: 3x3 rotation matrix
    # Simulating IMU frame to navigation frame transform
    angle = 0.5236  # 30 degrees in radians
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)

    # Rotation matrix (yaw-pitch-roll style)
    matrix = [
        [cos_a, -sin_a, 0.0],
        [sin_a, cos_a, 0.0],
        [0.0, 0.0, 1.0],
    ]
    # Spacecraft velocity vector
    vector = [1000.0, 2000.0, 500.0]

    iterations = 10000
    t0 = time.ticks_us()

    for _ in range(iterations):
        result = [0.0, 0.0, 0.0]
        for i in range(3):
            for j in range(3):
                result[i] += matrix[i][j] * vector[j]

    elapsed_us = time.ticks_diff(time.ticks_us(), t0)
    per_op = elapsed_us / iterations

    lcd.show("Nav transform:", f"[{result[0]:.0f},{result[1]:.0f},{result[2]:.0f}]")
    time.sleep(2)
    lcd.show(f"Pico: {per_op:.1f}us each", f"10K solves:{elapsed_us // 1000}ms")
    time.sleep(2)
    lcd.show("AGC: ~500us each", "Pico: much faster")
    time.sleep(2)


# --- Demo 7: Mandelbrot ---
def mandelbrot():
    title("[7] Mandelbrot", "Fractal compute")
    time.sleep(1)

    # Characters by density
    chars = " .:-=+*#%@"
    max_iter = 50

    lcd.show("Zooming into", "the fractal...")
    time.sleep(1)

    # Animate several rows at different y values
    for frame in range(20):
        y_c = -1.0 + frame * 0.1
        line = ""
        for col in range(16):
            x_c = -2.0 + col * 0.25
            x, y = 0.0, 0.0
            it = 0
            while x * x + y * y <= 4.0 and it < max_iter:
                x, y = x * x - y * y + x_c, 2 * x * y + y_c
                it += 1
            idx = min(it * len(chars) // (max_iter + 1), len(chars) - 1)
            line += chars[idx]

        lcd.show(line, f"y={y_c:.1f} iter={max_iter}")
        time.sleep_ms(400)

    lcd.show("1980: needed a", "mainframe for this")
    time.sleep(2)
    lcd.show("Pico does it", "in real-time!")
    time.sleep(2)


# --- Main ---
lcd.show("  PICO vs AGC", " Computer Power!")
time.sleep(3)
lcd.show("Apollo computer:", "2MHz 4KB $150K")
time.sleep(2)
lcd.show("Pico RP2040:", "133MHz 264KB $4")
time.sleep(2)
lcd.show("  Pico is", " 2800x faster!")
time.sleep(2)

demos = [pi_digits, prime_sieve, monte_carlo, trajectory,
         factorials, matrix_nav, mandelbrot]

print("Apollo vs Pico demo running!")

while True:
    for demo in demos:
        try:
            demo()
        except Exception as e:
            lcd.show("Error:", str(e)[:16])
            time.sleep(2)
        lcd.show("", "")
        time.sleep(0.5)

    lcd.show("  === LOOP ===", "  Restarting...")
    time.sleep(2)
