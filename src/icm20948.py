# ICM-20948 MicroPython driver for Raspberry Pi Pico
# I2C interface, AK09916 magnetometer via bypass mode
# No external dependencies — stdlib only

import struct
import time


class ICM20948Error(Exception):
    pass


class ICM20948:
    ICM_ADDR = 0x68   # AD0=GND; use 0x69 if AD0=VCC
    AK_ADDR  = 0x0C   # AK09916 magnetometer

    # Bank 0
    _WHO_AM_I     = 0x00
    _PWR_MGMT_1   = 0x06
    _PWR_MGMT_2   = 0x07
    _INT_PIN_CFG  = 0x0F
    _ACCEL_XOUT_H = 0x2D
    _TEMP_OUT_H   = 0x39
    _REG_BANK_SEL = 0x7F

    # Bank 2
    _GYRO_CONFIG_1      = 0x01
    _ACCEL_SMPLRT_DIV_1 = 0x10
    _ACCEL_SMPLRT_DIV_2 = 0x11
    _ACCEL_CONFIG       = 0x14

    # AK09916
    _AK_WIA2  = 0x01
    _AK_ST1   = 0x10
    _AK_HXL   = 0x11
    _AK_CNTL2 = 0x31
    _AK_CNTL3 = 0x32

    # Scale factors
    _ACCEL_SCALE = 16384.0   # LSB/g   for ±2g
    _GYRO_SCALE  =   131.0   # LSB/dps for ±250dps
    _MAG_SCALE   =     0.15  # μT/LSB
    _TEMP_SCALE  =   333.87
    _TEMP_OFFSET =    21.0

    def __init__(self, i2c, addr=None):
        self._i2c = i2c
        self._addr = addr or self.ICM_ADDR
        self._init_imu()
        self._init_mag()

    # ── Register I/O ────────────────────────────────

    def _bank(self, bank):
        self._i2c.writeto_mem(self._addr, self._REG_BANK_SEL, bytes([(bank & 0x03) << 4]))

    def _wr(self, reg, val):
        self._i2c.writeto_mem(self._addr, reg, bytes([val]))

    def _rd(self, reg, n=1):
        return self._i2c.readfrom_mem(self._addr, reg, n)

    def _ak_wr(self, reg, val):
        self._i2c.writeto_mem(self.AK_ADDR, reg, bytes([val]))

    def _ak_rd(self, reg, n=1):
        return self._i2c.readfrom_mem(self.AK_ADDR, reg, n)

    # ── Initialisation ──────────────────────────────

    def _init_imu(self):
        self._bank(0)
        who = self._rd(self._WHO_AM_I)[0]
        if who != 0xEA:
            raise ICM20948Error(f"WHO_AM_I=0x{who:02X}, expected 0xEA")

        self._wr(self._PWR_MGMT_1, 0x80)   # soft reset
        time.sleep_ms(50)
        self._wr(self._PWR_MGMT_1, 0x01)   # wake + auto-clock
        time.sleep_ms(30)
        self._wr(self._PWR_MGMT_2, 0x00)   # enable all axes

        self._bank(2)
        self._wr(self._GYRO_CONFIG_1, 0x19)      # ±250 dps, DLPF ~51 Hz
        self._wr(self._ACCEL_CONFIG, 0x19)       # ±2 g,     DLPF ~50 Hz
        self._wr(self._ACCEL_SMPLRT_DIV_1, 0x00)
        self._wr(self._ACCEL_SMPLRT_DIV_2, 0x00)

        self._bank(0)
        self._wr(self._INT_PIN_CFG, 0x02)   # BYPASS_EN → direct AK09916 access

    def _init_mag(self):
        wia = self._ak_rd(self._AK_WIA2)[0]
        if wia != 0x09:
            raise ICM20948Error(f"AK09916 WIA2=0x{wia:02X}, expected 0x09")
        self._ak_wr(self._AK_CNTL3, 0x01)   # soft reset
        time.sleep_ms(10)
        self._ak_wr(self._AK_CNTL2, 0x08)   # continuous mode 4 (100 Hz)
        time.sleep_ms(10)

    # ── Sensor Reads ────────────────────────────────

    def read_accel_gyro(self):
        """Returns (ax, ay, az) in g, (gx, gy, gz) in dps."""
        self._bank(0)
        raw = self._rd(self._ACCEL_XOUT_H, 12)
        ax, ay, az, gx, gy, gz = struct.unpack('>hhhhhh', raw)
        return (
            ax / self._ACCEL_SCALE, ay / self._ACCEL_SCALE, az / self._ACCEL_SCALE,
            gx / self._GYRO_SCALE,  gy / self._GYRO_SCALE,  gz / self._GYRO_SCALE,
        )

    def read_temp(self):
        """Returns die temperature in °C."""
        self._bank(0)
        t = struct.unpack('>h', self._rd(self._TEMP_OUT_H, 2))[0]
        return t / self._TEMP_SCALE + self._TEMP_OFFSET

    def read_mag(self):
        """Returns (mx, my, mz) in μT, or None if data not ready / overflow."""
        if not (self._ak_rd(self._AK_ST1)[0] & 0x01):
            return None
        raw = self._ak_rd(self._AK_HXL, 8)
        if raw[7] & 0x08:   # HOFL
            return None
        mx, my, mz = struct.unpack('<hhh', raw[:6])
        return mx * self._MAG_SCALE, my * self._MAG_SCALE, mz * self._MAG_SCALE

    def read_all(self):
        """Returns dict: accel (g), gyro (dps), mag (μT|None), temp (°C)."""
        ax, ay, az, gx, gy, gz = self.read_accel_gyro()
        return {
            'accel': (ax, ay, az),
            'gyro':  (gx, gy, gz),
            'mag':   self.read_mag(),
            'temp':  self.read_temp(),
        }
