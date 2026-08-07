"""Monocular distance estimation.

The math (pinhole camera model)
-------------------------------
A vehicle of real height H metres at distance D metres projects to a
bounding box of height h pixels:

    h = f * H / D    =>    D = f * H / h

where f is the focal length in pixels. f can be derived from the
horizontal field of view and image width:

    f = (image_width / 2) / tan(FoV_h / 2)

Accuracy notes
--------------
- The assumed vehicle height (1.5 m) is wrong for trucks/motorcycles, so
  absolute distance can be off by 20-40% for those classes. For a
  *threshold* alert this matters less than consistency; calibrating f
  against a known distance (docs/CALIBRATION.md) fixes most of the bias.
- Bbox height jitters frame to frame; exponential smoothing per track
  damps it before the decision logic sees it.
- Upgrade path: a VL53L1X time-of-flight sensor on I2C gives true
  distance up to ~4 m; longer range needs radar. The interface here is
  deliberately narrow (track -> distance in metres) so a sensor fusion
  version can swap in without touching the decision logic.
"""

from __future__ import annotations

import math

from config import CameraConfig, DistanceConfig
from detector import TrackedVehicle


class DistanceEstimator:
    def __init__(self, dist_cfg: DistanceConfig, cam_cfg: CameraConfig):
        self.cfg = dist_cfg
        if dist_cfg.calibrated_focal_length_px is not None:
            self.focal_px = dist_cfg.calibrated_focal_length_px
        else:
            fov_rad = math.radians(cam_cfg.horizontal_fov_deg)
            self.focal_px = (cam_cfg.width / 2.0) / math.tan(fov_rad / 2.0)
        self._smoothed: dict[int, float] = {}

    def estimate(self, vehicle: TrackedVehicle) -> float:
        """Return smoothed distance in metres for one tracked vehicle."""
        h = max(vehicle.bbox_height, 1.0)
        raw = self.focal_px * self.cfg.assumed_vehicle_height_m / h

        prev = self._smoothed.get(vehicle.track_id)
        if prev is None:
            smoothed = raw
        else:
            a = self.cfg.smoothing_alpha
            smoothed = a * raw + (1.0 - a) * prev
        self._smoothed[vehicle.track_id] = smoothed
        return smoothed

    def forget(self, active_ids: set[int]) -> None:
        """Drop smoothing state for tracks that disappeared."""
        for tid in list(self._smoothed):
            if tid not in active_ids:
                del self._smoothed[tid]
