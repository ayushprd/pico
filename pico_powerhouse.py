from machine import Pin, I2C, ADC
from lcd_i2c import LCD
import time, random, math

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=100000)
lcd = LCD(i2c, addr=0x27)


def title(line1, line2, pause=2):
    lcd.show(line1, line2)
    time.sleep(pause)


def gauss(mu=0, sigma=1):
    """Box-Muller transform — MicroPython has no random.gauss"""
    u1 = random.random()
    u2 = random.random()
    while u1 == 0:
        u1 = random.random()
    z = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
    return mu + sigma * z


# --- 1. SHA-256 Hash (Cryptography) ---
def sha256_demo():
    """Pure MicroPython SHA-256 — the backbone of Bitcoin, TLS, passwords"""
    title("[1] SHA-256", "Cryptography!")

    # SHA-256 constants
    K = [
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
        0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
        0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
        0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
        0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
        0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
        0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
        0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
        0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
        0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
        0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3,
        0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
        0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5,
        0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
        0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
        0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
    ]
    M = 0xFFFFFFFF

    def rr(v, n):
        return ((v >> n) | (v << (32 - n))) & M

    def sha256(msg):
        msg = bytearray(msg, 'utf-8') if isinstance(msg, str) else bytearray(msg)
        l = len(msg) * 8
        msg.append(0x80)
        while len(msg) % 64 != 56:
            msg.append(0)
        msg += l.to_bytes(8, 'big')

        h0, h1, h2, h3 = 0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a
        h4, h5, h6, h7 = 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19

        for i in range(0, len(msg), 64):
            w = [int.from_bytes(msg[i + j:i + j + 4], 'big') for j in range(0, 64, 4)]
            for j in range(16, 64):
                s0 = rr(w[j-15], 7) ^ rr(w[j-15], 18) ^ (w[j-15] >> 3)
                s1 = rr(w[j-2], 17) ^ rr(w[j-2], 19) ^ (w[j-2] >> 10)
                w.append((w[j-16] + s0 + w[j-7] + s1) & M)

            a, b, c, d, e, f, g, h = h0, h1, h2, h3, h4, h5, h6, h7
            for j in range(64):
                S1 = rr(e, 6) ^ rr(e, 11) ^ rr(e, 25)
                ch = (e & f) ^ (~e & M & g)
                t1 = (h + S1 + ch + K[j] + w[j]) & M
                S0 = rr(a, 2) ^ rr(a, 13) ^ rr(a, 22)
                maj = (a & b) ^ (a & c) ^ (b & c)
                t2 = (S0 + maj) & M
                h, g, f, e = g, f, e, (d + t1) & M
                d, c, b, a = c, b, a, (t1 + t2) & M

            h0, h1, h2, h3 = (h0+a)&M, (h1+b)&M, (h2+c)&M, (h3+d)&M
            h4, h5, h6, h7 = (h4+e)&M, (h5+f)&M, (h6+g)&M, (h7+h)&M

        return ''.join(f'{x:08x}' for x in [h0,h1,h2,h3,h4,h5,h6,h7])

    msg = "Hello from Pico"
    t0 = time.ticks_ms()
    h = sha256(msg)
    elapsed = time.ticks_diff(time.ticks_ms(), t0)

    lcd.show("SHA-256 hash:", f"  Done in {elapsed}ms")
    time.sleep(2)

    # Scroll the hash
    for i in range(len(h) - 15):
        lcd.show(h[i:i + 16], "Secures internet")
        time.sleep_ms(250)
    time.sleep(1)

    # Hash rate
    t0 = time.ticks_ms()
    for _ in range(20):
        sha256(msg)
    elapsed = time.ticks_diff(time.ticks_ms(), t0)
    rate = 20000 // elapsed

    lcd.show(f"{rate} hashes/sec", "Bitcoin uses this")
    time.sleep(3)


# --- 2. Kalman Filter (GPS/Navigation) ---
def kalman_demo():
    """1D Kalman filter — used in GPS, rockets, self-driving cars"""
    title("[2] Kalman Filtr", "GPS Navigation!")

    # Simulate noisy position measurements and filter them
    true_pos = 0.0
    true_vel = 2.0  # m/s
    dt = 0.1

    # Kalman state
    x = 0.0  # estimated position
    v = 0.0  # estimated velocity
    P = [[1.0, 0.0], [0.0, 1.0]]  # covariance
    Q = [[0.01, 0.0], [0.0, 0.01]]  # process noise
    R = 5.0  # measurement noise

    lcd.show("Noisy GPS data", "-> clean output")
    time.sleep(2)

    for step in range(80):
        # True physics
        true_pos += true_vel * dt

        # Noisy measurement
        z = true_pos + gauss(0, math.sqrt(R))

        # Predict
        x_pred = x + v * dt
        v_pred = v
        P[0][0] = P[0][0] + dt * (P[1][0] + P[0][1]) + dt * dt * P[1][1] + Q[0][0]
        P[0][1] = P[0][1] + dt * P[1][1]
        P[1][0] = P[1][0] + dt * P[1][1]
        P[1][1] = P[1][1] + Q[1][1]

        # Update
        S = P[0][0] + R
        K0 = P[0][0] / S
        K1 = P[1][0] / S
        y = z - x_pred
        x = x_pred + K0 * y
        v = v_pred + K1 * y
        P[0][0] = (1 - K0) * P[0][0]
        P[0][1] = (1 - K0) * P[0][1]
        P[1][0] = P[1][0] - K1 * P[0][0]
        P[1][1] = P[1][1] - K1 * P[0][1]

        err = abs(x - true_pos)
        noise = abs(z - true_pos)

        if step % 4 == 0:
            lcd.show(f"GPS:{z:6.1f} e={noise:.1f}", f"Flt:{x:6.1f} e={err:.2f}")
            time.sleep_ms(200)

    lcd.show("Kalman: used in", "every spacecraft")
    time.sleep(2)
    lcd.show("GPS, drones,", "self-driving car")
    time.sleep(2)


# --- 3. FFT (Signal Processing) ---
def fft_demo():
    """Radix-2 FFT — used in audio, radio, medical imaging"""
    title("[3] FFT", "Signal Analysis!")

    N = 256

    # Generate test signal: mix of frequencies
    signal_r = [0.0] * N
    signal_i = [0.0] * N
    for i in range(N):
        t = i / N
        signal_r[i] = (math.sin(2 * math.pi * 10 * t) +
                        0.5 * math.sin(2 * math.pi * 30 * t) +
                        0.3 * math.sin(2 * math.pi * 50 * t))

    lcd.show("Signal: 10+30+", "50 Hz mixed")
    time.sleep(2)

    # In-place FFT
    t0 = time.ticks_ms()

    # Bit-reversal permutation
    j = 0
    for i in range(1, N):
        bit = N >> 1
        while j & bit:
            j ^= bit
            bit >>= 1
        j ^= bit
        if i < j:
            signal_r[i], signal_r[j] = signal_r[j], signal_r[i]
            signal_i[i], signal_i[j] = signal_i[j], signal_i[i]

    # FFT butterfly
    length = 2
    while length <= N:
        angle = -2 * math.pi / length
        wr, wi = math.cos(angle), math.sin(angle)
        for i in range(0, N, length):
            w_r, w_i = 1.0, 0.0
            for k in range(length // 2):
                u_r = signal_r[i + k]
                u_i = signal_i[i + k]
                v_r = signal_r[i + k + length // 2] * w_r - signal_i[i + k + length // 2] * w_i
                v_i = signal_r[i + k + length // 2] * w_i + signal_i[i + k + length // 2] * w_r
                signal_r[i + k] = u_r + v_r
                signal_i[i + k] = u_i + v_i
                signal_r[i + k + length // 2] = u_r - v_r
                signal_i[i + k + length // 2] = u_i - v_i
                w_r, w_i = w_r * wr - w_i * wi, w_r * wi + w_i * wr
        length *= 2

    elapsed = time.ticks_diff(time.ticks_ms(), t0)

    # Find peaks
    magnitudes = [math.sqrt(signal_r[i]**2 + signal_i[i]**2) for i in range(N // 2)]
    peaks = []
    for i in range(2, N // 2 - 1):
        if magnitudes[i] > magnitudes[i-1] and magnitudes[i] > magnitudes[i+1] and magnitudes[i] > 10:
            peaks.append(i)

    lcd.show(f"256pt FFT:{elapsed}ms", f"Peaks: {peaks[:4]}")
    time.sleep(2)

    # Show magnitude spectrum on LCD using bar chars
    chars = " ._-~=*#@"
    max_m = max(magnitudes[:64])
    line = ""
    for col in range(16):
        idx = col * 4
        val = magnitudes[idx] / max_m if max_m > 0 else 0
        ci = min(int(val * (len(chars) - 1)), len(chars) - 1)
        line += chars[ci]

    lcd.show(line, "Spectrum visual")
    time.sleep(3)
    lcd.show("FFT: MRI scans,", "WiFi, Bluetooth")
    time.sleep(2)


# --- 4. Linear Regression (Data Science) ---
def regression_demo():
    """Least squares regression — foundation of machine learning"""
    title("[4] Regression", "Data Science!")

    # Generate noisy linear data: y = 2.5x + 10 + noise
    n = 200
    true_slope = 2.5
    true_intercept = 10.0

    t0 = time.ticks_ms()

    sum_x = 0.0
    sum_y = 0.0
    sum_xy = 0.0
    sum_x2 = 0.0

    for i in range(n):
        x = i * 0.1
        y = true_slope * x + true_intercept + gauss(0, 2.0)
        sum_x += x
        sum_y += y
        sum_xy += x * y
        sum_x2 += x * x

    # Solve normal equations
    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
    intercept = (sum_y - slope * sum_x) / n

    elapsed = time.ticks_diff(time.ticks_ms(), t0)

    lcd.show(f"y={slope:.2f}x+{intercept:.1f}", f"True:2.50x+10.0")
    time.sleep(3)
    lcd.show(f"{n}pts in {elapsed}ms", "ML starts here!")
    time.sleep(2)


# --- 5. PID Controller (Robotics/Industrial) ---
def pid_demo():
    """PID controller — runs every factory, drone, thermostat"""
    title("[5] PID Control", "Robotics!")

    # Simulate temperature control: target 75C
    target = 75.0
    temp = 20.0  # start at room temp
    dt = 0.1

    # PID gains
    Kp, Ki, Kd = 2.0, 0.5, 1.0
    integral = 0.0
    prev_error = target - temp

    lcd.show("Target: 75.0 C", "Start:  20.0 C")
    time.sleep(2)

    for step in range(100):
        error = target - temp
        integral += error * dt
        derivative = (error - prev_error) / dt
        prev_error = error

        output = Kp * error + Ki * integral + Kd * derivative
        output = max(0, min(100, output))  # clamp heater 0-100%

        # Plant model: heater warms, environment cools
        temp += (output * 0.05 - (temp - 20) * 0.02) * dt

        if step % 5 == 0:
            lcd.show(f"T:{temp:5.1f}C tgt:75C", f"Heater: {output:5.1f}%")
            time.sleep_ms(150)

    lcd.show(f"Settled: {temp:.1f}C", "PID: everywhere!")
    time.sleep(2)
    lcd.show("Drones, rockets,", "your thermostat")
    time.sleep(2)


# --- 6. Sorting Race ---
def sort_demo():
    """Quicksort 1000 numbers — databases, search engines"""
    title("[6] Quicksort", "1000 numbers!")

    data = [random.randint(0, 99999) for _ in range(1000)]

    lcd.show("Shuffled 1000", "random numbers")
    time.sleep(1)

    # Iterative quicksort (avoid stack overflow)
    t0 = time.ticks_ms()

    arr = list(data)
    stack = [(0, len(arr) - 1)]
    while stack:
        lo, hi = stack.pop()
        if lo >= hi:
            continue
        pivot = arr[hi]
        i = lo
        for j in range(lo, hi):
            if arr[j] <= pivot:
                arr[i], arr[j] = arr[j], arr[i]
                i += 1
        arr[i], arr[hi] = arr[hi], arr[i]
        stack.append((lo, i - 1))
        stack.append((i + 1, hi))

    elapsed = time.ticks_diff(time.ticks_ms(), t0)

    lcd.show(f"Sorted in {elapsed}ms", f"Min:{arr[0]} Max:{arr[-1]}")
    time.sleep(2)

    # Verify
    ok = all(arr[i] <= arr[i+1] for i in range(len(arr) - 1))
    lcd.show(f"Verified: {'OK!' if ok else 'FAIL'}", "Search engines")
    time.sleep(1)
    lcd.show("use this billions", "of times per day")
    time.sleep(2)


# --- 7. Fibonacci / Golden Ratio ---
def fibonacci_demo():
    """Big Fibonacci — number theory, nature's pattern"""
    title("[7] Fibonacci", "Nature's math!")

    t0 = time.ticks_ms()
    a, b = 0, 1
    n = 0
    while n < 300:
        a, b = b, a + b
        n += 1
    elapsed = time.ticks_diff(time.ticks_ms(), t0)

    fib_str = str(a)
    ratio = b / a if a else 0

    lcd.show(f"F(300)={len(fib_str)}digs", f"in {elapsed}ms")
    time.sleep(2)

    lcd.show("Golden ratio:", f"  {ratio:.12f}"[:16])
    time.sleep(2)

    # Scroll the number
    lcd.show(f"F(300):", "")
    for i in range(min(len(fib_str) - 15, 40)):
        lcd.move_to(0, 1)
        lcd.putstr(fib_str[i:i + 16])
        time.sleep_ms(200)
    time.sleep(1)

    lcd.show("Fibonacci is in", "flowers, shells")
    time.sleep(2)


# --- 8. Numerical ODE: Lorenz Attractor (Chaos Theory) ---
def lorenz_demo():
    """Lorenz attractor — chaos theory, weather prediction"""
    title("[8] Chaos Theory", "Lorenz Attractor")

    # Lorenz system parameters
    sigma = 10.0
    rho = 28.0
    beta = 8.0 / 3.0
    dt = 0.005

    x, y, z = 1.0, 1.0, 1.0

    t0 = time.ticks_ms()

    for step in range(4000):
        dx = sigma * (y - x)
        dy = x * (rho - z) - y
        dz = x * y - beta * z
        x += dx * dt
        y += dy * dt
        z += dz * dt

        if step % 200 == 0:
            lcd.show(f"x={x:7.2f}", f"y={y:7.2f} z={z:5.1f}")
            time.sleep_ms(150)

    elapsed = time.ticks_diff(time.ticks_ms(), t0)

    lcd.show(f"4000 steps:{elapsed}ms", "Butterfly effect")
    time.sleep(2)
    lcd.show("Tiny change ->", "totally diff path")
    time.sleep(2)
    lcd.show("Why weather is", "hard to predict!")
    time.sleep(2)


# --- Main ---
lcd.show(" PICO POWERHOUSE", "Real Computations")
time.sleep(3)
lcd.show("Things that run", "our modern world")
time.sleep(2)

demos = [sha256_demo, kalman_demo, fft_demo, regression_demo,
         pid_demo, sort_demo, fibonacci_demo, lorenz_demo]

print("Pico Powerhouse demo running!")

while True:
    for demo in demos:
        try:
            demo()
        except Exception as e:
            lcd.show("Error:", str(e)[:16])
            print(f"Error in demo: {e}")
            time.sleep(2)
        lcd.show("", "")
        time.sleep(0.5)

    lcd.show("=== LOOP ===", "Restarting...")
    time.sleep(2)
