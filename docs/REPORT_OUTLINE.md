# Engineering Report — Outline & Research Direction

Skeleton for the final report (target 12–20 pages). Poster and slides
derive from the same structure.

1. **Abstract** — problem, approach, headline results (precision/recall,
   FPS, latency).
2. **Introduction & motivation** — rear-end collisions and tailgating as
   a factor; gap: production rear collision warning exists in new cars,
   not affordable retrofits.
3. **Related work** — see below.
4. **System design** — architecture diagram; hardware selection
   rationale (why Pi 5 / Camera Module 3 / BLE); enclosure design.
5. **Methodology** — YOLO26n choice & benchmarks; ByteTrack; pinhole
   distance model + calibration procedure; decision algorithm with the
   violation-ratio justification.
6. **Implementation** — module structure, offline-first constraints, BLE
   GATT design.
7. **Evaluation** — full metrics table from docs/TESTING.md; edge-case
   findings; thermal/power results.
8. **Limitations** — monocular depth assumptions, night performance,
   class-height bias, not a certified safety system.
9. **Future work** — ToF/radar fusion, Hailo acceleration, per-class
   heights, lane detection for curved-road filtering.
10. **Conclusion**, references, appendices (BOM, wiring, code listing).

## Research to cite (search terms → what it supports)

Find these on Google Scholar / arXiv and pick recent, well-cited
representatives — verify details before citing:

| Topic / search terms | Supports which section |
|---|---|
| "monocular distance estimation vehicle detection" | Methodology: pinhole model precedent & known error sources |
| "vision-based forward collision warning system" | Related work: the front-facing mirror of this project |
| "rear-end collision warning system" + NHTSA rear-end crash statistics | Motivation: problem scale |
| "ByteTrack multi-object tracking" (Zhang et al.) | Methodology: tracker choice |
| Ultralytics YOLO26 paper (arXiv 2606.03748) + "YOLO evolution overview" (arXiv 2510.09653) | Methodology: detector choice, NMS-free edge inference |
| "embedded deep learning inference Raspberry Pi benchmark" | Implementation: edge-AI feasibility |
| "time headway tailgating definition traffic safety" | Decision algorithm: the 2-second rule / headway literature justifies distance-x-time thresholds |
| "ADAS SAE J3016 levels" | Intro: where this sits (Level 0 warning system) |

Tip: the *time-headway* literature is the strongest academic anchor for
your decision rule — traffic engineering defines tailgating in seconds
of headway, not meters, which motivates a future version that scales
distance_threshold with ego speed (needs GPS/OBD speed input — good
future-work paragraph).
