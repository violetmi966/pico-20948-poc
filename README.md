# Raspberry Pi Pico × ICM-20948 PoC

[![GitHub](https://img.shields.io/badge/GitHub-pico--20948--poc-blue?logo=github)](https://github.com/ChunPingWang/pico-20948-poc)

Raspberry Pi Pico 整合 TDK ICM-20948 九軸 IMU 的概念驗證專案（MicroPython）。  
Pico 原生 3.3V 輸出，**不需要電位轉換電路**，可直接接裸模組或分接板。

---

## 硬體需求

| 元件 | 規格 | 備註 |
|------|------|------|
| Raspberry Pi Pico | 任意版本 | 3.3V I/O |
| ICM-20948 模組 | 裸模組或分接板皆可 | 直接 3.3V 供電 |
| 4.7 kΩ 電阻 × 2 | ¼W | I2C pull-up（若板上無） |
| 100 nF 電容 × 2 | 陶瓷 | VCC 去耦電容 |

> Pico 與 Arduino Uno 最大差異：Pico 為 3.3V 系統，**無需**電位轉換，電路更簡單。

---

## 接線（I2C0）

```
Pico                        ICM-20948
────────────────────────────────────────
3V3  (pin 36) ──────────── VCC
GND  (pin 38) ──────────── GND
GP4  (pin  6) ──[4.7kΩ]── SDA  (pull-up to 3.3V)
GP5  (pin  7) ──[4.7kΩ]── SCL  (pull-up to 3.3V)
GP15 (pin 20) ──────────── INT  (可選，資料就緒中斷)
                            AD0 ── GND  → I2C 位址 0x68
                            AD0 ── 3V3  → I2C 位址 0x69
```

若使用其他 I2C 腳位，修改 `main.py` 中的 `I2C(0, sda=Pin(x), scl=Pin(y))`。  
Pico 支援的 I2C0 腳位：GP0/GP1、GP4/GP5、GP8/GP9、GP12/GP13、GP16/GP17、GP20/GP21。

---

## 專案結構

```
.
├── src/
│   ├── icm20948.py     # ICM-20948 MicroPython 驅動（含 AK09916）
│   └── main.py         # 50 Hz CSV 輸出示範
└── validation/
    └── validation.py   # 8 項自動化驗證測試
```

---

## 使用說明

### 環境準備

1. 安裝 [Thonny IDE](https://thonny.org/) 或使用 `mpremote`。
2. 燒錄 MicroPython 韌體至 Pico（[官方下載](https://micropython.org/download/RPI_PICO/)）。

### 執行主程式

```bash
# 使用 mpremote 複製檔案
mpremote cp src/icm20948.py :icm20948.py
mpremote cp src/main.py     :main.py
mpremote run src/main.py
```

或透過 Thonny 開啟並執行 `main.py`。

輸出格式（CSV，可貼入 Serial Plotter）：
```
ax(g),ay(g),az(g),gx(dps),gy(dps),gz(dps),mx(uT),my(uT),mz(uT),temp(C)
0.002,0.001,0.999,-0.08,0.12,-0.03,18.45,-32.10,25.60,27.3
```

感測器設定：
- 加速度計：±2 g，DLPF ≈ 50 Hz
- 陀螺儀：±250 dps，DLPF ≈ 51 Hz
- 磁力計（AK09916）：100 Hz 連續模式，I2C bypass 直接存取
- 輸出率：50 Hz

### API

```python
from machine import I2C, Pin
from icm20948 import ICM20948

i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=400_000)
imu = ICM20948(i2c)

ax, ay, az, gx, gy, gz = imu.read_accel_gyro()  # g, dps
mag  = imu.read_mag()    # (mx, my, mz) μT 或 None
temp = imu.read_temp()   # °C
data = imu.read_all()    # dict: accel / gyro / mag / temp
```

---

## 驗證測試

感測器**水平靜置，Z 軸朝上**：

```bash
mpremote cp src/icm20948.py  :icm20948.py
mpremote cp validation/validation.py :validation.py
mpremote run validation/validation.py
```

| 測試 | 項目 | 通過條件 |
|:----:|------|----------|
| T1 | WHO_AM_I 識別 | `0xEA` |
| T2 | AK09916 識別 + init | `0x09` |
| T3 | 靜態加速度 Z 軸 | `0.90 g ≤ az ≤ 1.10 g` |
| T4 | 靜態加速度 XY 軸 | `\|ax\|, \|ay\| < 0.10 g` |
| T5 | 靜態陀螺儀雜訊 | 峰值 `< 2.0 dps` |
| T6 | 地磁場大小 | `20 ≤ \|B\| ≤ 80 μT` |
| T7 | 溫度合理性 | `10–50 °C` |
| T8 | 輸出資料率 | `45–55 Hz` |

---

## 與 Arduino Uno 版本比較

| 項目 | Arduino Uno | Raspberry Pi Pico |
|------|:-----------:|:-----------------:|
| 電壓 | 5V（需電位轉換） | 3.3V（直接連接） |
| 語言 | C++ (Arduino) | MicroPython |
| I2C 腳位 | A4/A5（固定） | 任意 GP 腳位 |
| 程式部署 | USB 燒錄 | 拖放 / mpremote |
| 函式庫 | SparkFun 或自行實作 | 本 repo 驅動 |

---

## 相關專案

- [mcu-20948-poc](https://github.com/ChunPingWang/mcu-20948-poc) — Arduino Uno 版本（C++，含暫存器直接操作）

---

## 授權

MIT
