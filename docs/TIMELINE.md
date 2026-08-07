# Project Timeline & Risk Assessment

Assumes ~8–10 hrs/week alongside classes. 8 weeks to a demo-ready system.

| Week | Milestone | Deliverable |
|------|-----------|-------------|
| 1 | Hardware bring-up | Pi boots, camera verified (`rpicam-hello`), repo pushed |
| 2 | Detection running | YOLO26n on live camera, FPS benchmarked at 320/640 |
| 3 | Tracking + distance | Stable track IDs; calibrated distance within ±20% static |
| 4 | Decision logic | Unit tests pass; tuned on first recorded footage |
| 5 | BLE pipeline | Alert lands in nRF Connect end-to-end; latency measured |
| 6 | Enclosure + install | Case printed, mounted in vehicle, thermal/power validated |
| 7 | Validation | Tier 2–4 testing, metrics table filled in |
| 8 | Documentation | Report, README polish, demo video, poster/slides |

Stretch (weeks 9+): Flutter app, ToF sensor fusion, dashcam recording.

## Risk assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| FPS too low on Pi CPU | Medium | High | imgsz=320, yolo26n; escalate to Hailo AI Kit ($70) |
| Distance too inaccurate | Medium | Medium | Calibration; threshold-based design tolerates bias; ToF upgrade path |
| BLE drops in-vehicle | Low | Medium | Peripheral keeps advertising; phone auto-resubscribes; test Tier 3 |
| Thermal throttling in car | Medium | Medium | Active cooler, vented PETG case, thermal soak test |
| Undervoltage from car adapter | Medium | High | Spec'd 5V/5A PD adapter; `get_throttled` check in Tier 3 |
| SD corruption from power cuts | Medium | Low | Overlay filesystem (read-only root) |
| False positives annoy driver | Medium | Medium | violation_ratio + cooldown; tune on labeled footage first |
| Scope creep (app, extra features) | High | Medium | nRF Connect is the v1 phone client; Flutter is stretch only |
