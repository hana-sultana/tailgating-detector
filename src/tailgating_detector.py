"""Tailgating decision logic.

Decision rule (per tracked vehicle)
-----------------------------------
1. Lane filter: only consider vehicles whose bbox center is within a
   central horizontal band of the frame — a rear camera sees adjacent
   lanes too, and a close car one lane over is not tailgating.
2. Sliding window: keep (timestamp, distance) samples for the last
   time_threshold_s seconds.
3. Violation ratio: alert when the window spans the full time threshold
   AND >= violation_ratio of samples are below distance_threshold_m.
   Using a ratio instead of "every frame" means one missed detection or
   one jittery frame doesn't reset the clock — the main source of false
   NEGATIVES — while the ratio floor still rejects brief passes-by — the
   main source of false POSITIVES.
4. Cooldown: after alerting on a track, suppress further alerts for that
   track for alert_cooldown_s so the driver isn't spammed.

Pseudo-code
-----------
for each frame:
    for each tracked vehicle in center band:
        d = estimate_distance(vehicle)
        window[id].append((now, d))
        drop samples older than time_threshold_s
        if window spans time_threshold_s
           and fraction(d < distance_threshold_m) >= violation_ratio
           and now - last_alert[id] > cooldown:
                fire alert(id, d)
"""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass

from config import TailgatingConfig
from detector import TrackedVehicle


@dataclass
class TailgatingEvent:
    track_id: int
    distance_m: float
    duration_s: float
    timestamp: float


class TailgatingDetector:
    def __init__(self, cfg: TailgatingConfig, frame_width: int):
        self.cfg = cfg
        self.frame_width = frame_width
        self._windows: dict[int, deque[tuple[float, float]]] = {}
        self._last_alert: dict[int, float] = {}

    def _in_center_band(self, v: TrackedVehicle) -> bool:
        offset = abs(v.center_x - self.frame_width / 2.0) / self.frame_width
        return offset <= self.cfg.lane_center_band

    def update(
        self, vehicle: TrackedVehicle, distance_m: float, now: float | None = None
    ) -> TailgatingEvent | None:
        """Feed one (vehicle, distance) sample; return an event if it fires."""
        now = time.monotonic() if now is None else now

        if not self._in_center_band(vehicle):
            self._windows.pop(vehicle.track_id, None)
            return None

        window = self._windows.setdefault(vehicle.track_id, deque())
        window.append((now, distance_m))
        while window and now - window[0][0] > self.cfg.time_threshold_s:
            window.popleft()

        span = now - window[0][0] if window else 0.0
        if span < self.cfg.time_threshold_s * 0.95:
            return None  # not enough continuous history yet

        violations = sum(1 for _, d in window if d < self.cfg.distance_threshold_m)
        if violations / len(window) < self.cfg.violation_ratio:
            return None

        last = self._last_alert.get(vehicle.track_id)
        if last is not None and now - last < self.cfg.alert_cooldown_s:
            return None

        self._last_alert[vehicle.track_id] = now
        return TailgatingEvent(
            track_id=vehicle.track_id,
            distance_m=distance_m,
            duration_s=span,
            timestamp=time.time(),
        )

    def prune(self, active_ids: set[int]) -> None:
        """Drop state for tracks no longer present."""
        for tid in list(self._windows):
            if tid not in active_ids:
                del self._windows[tid]
        for tid in list(self._last_alert):
            if tid not in active_ids:
                del self._last_alert[tid]
