# Camera Calibration for Distance Estimation

The estimator uses the pinhole model: `D = f · H / h`, with focal length
`f` (pixels) derived from the FoV spec by default. A 10-minute one-point
calibration replaces the spec value with a measured one and removes most
systematic bias.

## One-point calibration (do this)

1. Park. Place a second car (or have a helper park) directly behind at a
   **measured** distance — tape-measure 10.0 m from lens to car front.
2. Run `python main.py --show` and read the bbox height `h_px` of that
   car from a saved event frame or by adding a debug print.
3. Compute: `f = D · h / H = 10.0 · h_px / 1.5`
4. Put the result in `config.py`:
   `calibrated_focal_length_px = <your f>`
5. Re-verify at 5 m and 15 m; error should be within ±15%.

## Expected accuracy

| Source of error | Magnitude | Mitigation |
|---|---|---|
| Vehicle height assumption (1.5 m) | ±20% car vs SUV | Per-class heights (future) |
| Bbox jitter | ±5–10% frame-to-frame | EMA smoothing (built in) |
| Lens distortion at frame edges | grows off-center | Lane filter keeps targets central |
| Pitch changes (braking/bumps) | transient | Time window absorbs transients |

For a *threshold-based* alert, consistency matters more than absolute
accuracy — calibrate once, then tune `distance_threshold_m` empirically
on real footage until alerts match your judgment of "too close".

## Full checkerboard calibration (optional, for the report)

OpenCV's `calibrateCamera` with a printed 9×6 checkerboard yields the
full intrinsic matrix + distortion coefficients — great material for the
engineering report's methodology section, and enables undistortion if
you switch to the Wide camera. See OpenCV's calibration tutorial;
~20 board poses is plenty.
