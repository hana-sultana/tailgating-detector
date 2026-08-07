# Wiring, Pinout, and Assembly

This build is deliberately low-wiring: two cables total in the base
configuration (camera ribbon + USB-C power). BLE replaces all signal
wiring to the driver.

## Connection map

```
[12V socket] --> [USB-C PD car adapter, 5V/5A] --USB-C--> [Pi 5 power in]

[Camera Module 3] ==22-pin ribbon (CAM/DISP 0)==> [Pi 5]

[Pi 5 BLE radio] ~~~~2.4 GHz~~~~> [Smartphone]
```

## Camera ribbon (the one fiddly step)

1. Pi 5 has two mini (22-pin) CSI ports labeled CAM/DISP 0 and 1 — use
   **CAM/DISP 0** (matches config default).
2. Ribbon contacts face **inward toward the USB ports** on the Pi side;
   on the camera side, contacts face the camera PCB. Blue stiffener
   faces away from contacts on both ends.
3. Lift the black latch, seat the ribbon fully and squarely, press the
   latch closed. A half-seated ribbon = "no camera found".
4. Verify: `rpicam-hello --list-cameras`

## Optional ToF sensor (VL53L1X, sensor-fusion upgrade)

| VL53L1X pin | Pi 5 pin (physical) | Function |
|-------------|---------------------|----------|
| VIN | 1 (3V3) | Power |
| GND | 6 (GND) | Ground |
| SDA | 3 (GPIO2/SDA1) | I2C data |
| SCL | 5 (GPIO3/SCL1) | I2C clock |

Enable I2C via `sudo raspi-config` → Interface Options. Verify with
`i2cdetect -y 1` (device at 0x29).

## Assembly order

1. Fit the active cooler to the Pi (before anything else — it needs
   clear board access).
2. Screw the Pi onto the base-tray standoffs (4× M2.5).
3. Route the camera ribbon out the side CSI slot in the base.
4. Connect USB-C through the IO slot.
5. Press the lid on; verify vents sit over the cooler.
6. Mount base to parcel shelf with zip ties through the floor channels
   (or VHB tape). Camera bracket mounts to the rear glass area, lens
   facing traffic, roughly level; zip-tie holes provided.

## In-vehicle placement notes

- Rear parcel shelf (sedan) or trunk-lid interior trim (hatch) both work;
  keep the lens unobstructed by the wiper/defroster lines where possible.
- Power from the 12 V socket means the system powers on with the
  ignition — no battery drain, and clean shutdown matters less because
  the filesystem sees mostly-read workloads once running (still: enable
  overlay filesystem in raspi-config for robustness against hard cuts).
