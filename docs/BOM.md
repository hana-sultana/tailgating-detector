# Bill of Materials

Prices are typical US retail as of mid-2026 — verify current pricing
before purchase.

| # | Item | Spec | Qty | Est. cost |
|---|------|------|-----|----------:|
| 1 | Raspberry Pi 5 | 8 GB (4 GB works; 8 GB gives headroom) | 1 | $80 |
| 2 | Raspberry Pi Camera Module 3 | Wide variant recommended (102° FoV) | 1 | $35 |
| 3 | CSI camera cable | Pi 5 uses 22-pin mini-CSI: get a "Pi 5 camera cable", 300–500 mm | 1 | $5 |
| 4 | microSD card | 64 GB, A2-rated (app performance class matters) | 1 | $12 |
| 5 | Active cooler | Official Raspberry Pi Active Cooler | 1 | $5 |
| 6 | Car power adapter | USB-C PD, must sustain 5 V/5 A (25 W) — most phone chargers won't | 1 | $20 |
| 7 | USB-C cable | Short, 5 A-rated | 1 | $8 |
| 8 | Enclosure | 3D-printed (hardware/cad/), ~80 g PETG | — | $3 |
| 9 | M2.5 screws + standoffs | Pi mounting, 6 mm | 4 | $3 |
| 10 | Zip ties / 3M VHB tape | Mounting to parcel shelf / trunk lid | — | $5 |
| | **Total** | | | **≈ $176** |

## Optional upgrades

| Item | Purpose | Est. cost |
|------|---------|----------:|
| VL53L1X ToF sensor | True distance ≤ 4 m over I2C (sensor-fusion upgrade) | $12 |
| Raspberry Pi AI Kit (Hailo-8L) | 10× inference speedup if you outgrow CPU FPS | $70 |
| USB battery bank (PD, 25 W) | Bench/field testing without the car | $30 |

## Material notes

- Print the enclosure in **PETG or ASA**, not PLA — a parked car's
  interior exceeds PLA's glass transition temperature (~60 °C) on a hot
  day and the case will warp.
- The official 27 W USB-C supply is the benchmark for what the car
  adapter must match; undervoltage throttles the Pi 5 hard during
  sustained inference.
