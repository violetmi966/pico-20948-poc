# ICM-20948 Validation Test Suite — MicroPython / Raspberry Pi Pico
#
# Keep sensor FLAT (Z-axis up) and STILL during the entire run.
# Copy icm20948.py to Pico root, then run this file.

from machine import I2C, Pin
import time
import math
from icm20948 import ICM20948, ICM20948Error

# ── Test framework ───────────────────────────────

_pass = 0
_fail = 0

def result(name, ok, detail=""):
    global _pass, _fail
    tag = "PASS" if ok else "FAIL"
    line = f"  [{tag}] {name}"
    if detail:
        line += f" — {detail}"
    print(line)
    if ok:
        _pass += 1
    else:
        _fail += 1

# ── Setup ────────────────────────────────────────

print("====================================")
print("  ICM-20948 Validation (Pico)")
print("====================================")
print("Place sensor FLAT (Z-up) and STILL.")
print("Starting in 3s...")
time.sleep(3)

i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=400_000)

# T1: WHO_AM_I (raw read before full init)
print("\nT1: WHO_AM_I identity")
i2c.writeto_mem(0x68, 0x7F, bytes([0x00]))   # bank 0
who = i2c.readfrom_mem(0x68, 0x00, 1)[0]
result("ICM-20948 WHO_AM_I", who == 0xEA, f"0x{who:02X} (want 0xEA)")

# T2: AK09916 + full init
print("T2: AK09916 identity + sensor init")
imu = None
try:
    imu = ICM20948(i2c)
    result("Sensor init + AK09916", True, "WIA2=0x09 verified")
except ICM20948Error as e:
    result("Sensor init + AK09916", False, str(e))

if imu is None:
    print(f"\nResult: {_pass} PASS / {_fail} FAIL  (aborted)")
    raise SystemExit

# ── Helper: collect N accel+gyro samples at ~50 Hz ──

def collect(n):
    samples = []
    for _ in range(n):
        samples.append(imu.read_accel_gyro())
        time.sleep_ms(20)
    return samples

# T3 + T4: Static accelerometer
print("T3+T4: Static accel (50 samples)")
s = collect(50)
avg_ax = sum(x[0] for x in s) / len(s)
avg_ay = sum(x[1] for x in s) / len(s)
avg_az = sum(x[2] for x in s) / len(s)
result("Accel Z ~1g",  0.90 <= avg_az <= 1.10, f"az={avg_az:.3f}g")
result("Accel X ~0g",  abs(avg_ax) < 0.10,     f"ax={avg_ax:.3f}g")
result("Accel Y ~0g",  abs(avg_ay) < 0.10,     f"ay={avg_ay:.3f}g")

# T5: Gyro static noise
print("T5: Gyro static noise (50 samples)")
peak = 0.0
for x in collect(50):
    peak = max(peak, abs(x[3]), abs(x[4]), abs(x[5]))
result("Gyro peak < 2 dps", peak < 2.0, f"peak={peak:.2f} dps")

# T6: Magnetometer Earth field
print("T6: Magnetometer Earth field (20 samples)")
mags = []
for _ in range(20):
    m = imu.read_mag()
    if m:
        mags.append(m)
    time.sleep_ms(15)
if mags:
    avg = [sum(m[i] for m in mags) / len(mags) for i in range(3)]
    total = math.sqrt(sum(v * v for v in avg))
    result("Mag field 20–80 μT", 20.0 <= total <= 80.0, f"|B|={total:.1f} μT")
else:
    result("Mag field 20–80 μT", False, "no DRDY samples")

# T7: Temperature sanity
print("T7: Temperature sanity")
temp = imu.read_temp()
result("Temperature 10–50 °C", 10.0 <= temp <= 50.0, f"{temp:.1f} °C")

# T8: Output data rate
print("T8: Output data rate (~50 Hz)")
N = 20
t0 = time.ticks_us()
for _ in range(N):
    imu.read_accel_gyro()
    time.sleep_ms(20)
elapsed_us = time.ticks_diff(time.ticks_us(), t0)
hz = N * 1_000_000 / elapsed_us
result("ODR 45–55 Hz", 45.0 <= hz <= 55.0, f"{hz:.1f} Hz")

# ── Summary ──────────────────────────────────────

print()
print("====================================")
print(f"  Result: {_pass} PASS  /  {_fail} FAIL")
print("====================================")
