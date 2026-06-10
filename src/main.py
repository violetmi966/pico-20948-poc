# Raspberry Pi Pico + ICM-20948 PoC
#
# Wiring (3.3V — no level shifter needed):
#   Pico 3V3 (pin 36) → VCC      Pico GND (pin 38) → GND
#   Pico GP4 (pin  6) → SDA      Pico GP5 (pin  7) → SCL
#   Pico GP15 (pin 20)→ INT  (optional)
#   AD0 → GND  →  I2C address 0x68
#
# Copy icm20948.py to Pico root before running.

from machine import I2C, Pin
import time
from icm20948 import ICM20948

i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=400_000)
imu = ICM20948(i2c)

print("ax(g),ay(g),az(g),gx(dps),gy(dps),gz(dps),mx(uT),my(uT),mz(uT),temp(C)")

while True:
    d = imu.read_all()
    ax, ay, az = d['accel']
    gx, gy, gz = d['gyro']
    temp       = d['temp']
    mag        = d['mag'] or (0.0, 0.0, 0.0)
    mx, my, mz = mag

    print(
        f"{ax:.3f},{ay:.3f},{az:.3f},"
        f"{gx:.2f},{gy:.2f},{gz:.2f},"
        f"{mx:.2f},{my:.2f},{mz:.2f},"
        f"{temp:.1f}"
    )
    time.sleep_ms(20)   # ~50 Hz
