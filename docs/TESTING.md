# Testing & Validation Plan

Four tiers, cheapest first. Never tune on public roads — tune on
recorded footage, then validate.

## Tier 1 — Unit tests (done, automated)

`pytest tests/ -v` covers the decision logic: sustained-close fires,
brief pass doesn't, far never, adjacent lane filtered, cooldown works,
jitter tolerated. Run on every commit (add GitHub Actions later).

## Tier 2 — Recorded-footage evaluation (main development loop)

1. Mount the camera, record 30–60 min of normal driving with
   `rpicam-vid` (varied: highway, city, night, rain if possible).
2. Hand-label tailgating segments (start/end timestamps) — your ground
   truth.
3. Run `python main.py --video clip.mp4`; compare fired events to labels.

**Metrics to report:**

| Metric | Definition | Target |
|---|---|---|
| Precision | true alerts / all alerts | ≥ 0.8 |
| Recall | true alerts / labeled events | ≥ 0.8 |
| Alert latency | time from threshold crossing to BLE notify | ≤ 1 s beyond time_threshold |
| Throughput | pipeline FPS on Pi 5 | ≥ 10 FPS at imgsz=320 |
| Distance error | vs tape measure at 5/10/15 m (static) | ≤ ±20% |

## Tier 3 — Static & parking-lot tests

- Distance accuracy: parked cars at measured distances (see CALIBRATION).
- BLE range/reliability: phone in cabin, Pi in trunk — alert delivery
  rate over 50 induced events; reconnection after walking out of range.
- Thermal soak: 30 min sustained inference; log
  `vcgencmd measure_temp` — must stay < 80 °C (throttle point 85 °C).
- Power: confirm no undervoltage flags (`vcgencmd get_throttled` → 0x0)
  on the car adapter.

## Tier 4 — On-road validation (passenger operates, driver drives)

Predefined, safe scenarios only — you never create tailgating yourself:
normal following traffic, stop-and-go, highway merge zones. Log
everything; review event snapshots afterward for false positives.

## Edge cases to test explicitly

- Motorcycles (smaller H → distance overestimated; note in report)
- Trucks/buses (larger H → underestimated; consider per-class heights)
- Night: headlight bloom; test detection confidence at night
- Rain on rear glass; defroster line occlusion
- Ego vehicle turning (lane filter behavior through curves)
- Vehicle approaching fast then backing off (should NOT alert)
- Two vehicles swapping (track ID switches — does cooldown map sensibly?)
- Tunnel/exposure swings; low sun directly into lens
- BLE: phone screen off, app backgrounded, phone rebooted mid-drive

## Stress tests

- 2-hour continuous run: memory RSS flat? (watch with `psutil`/`top`)
- Dense traffic clip (10+ vehicles/frame): FPS floor and latency
- SD card: overlay filesystem on, hard power-cut 10×, verify boot
