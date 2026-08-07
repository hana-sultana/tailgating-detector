"""Unit tests for the tailgating decision logic (pure logic, no hardware).

Run: pytest tests/ -v
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import TailgatingConfig
from detector import TrackedVehicle
from tailgating_detector import TailgatingDetector

FRAME_W = 1280
CFG = TailgatingConfig(
    distance_threshold_m=8.0,
    time_threshold_s=3.0,
    lane_center_band=0.25,
    alert_cooldown_s=20.0,
    violation_ratio=0.8,
)


def make_vehicle(track_id=1, center_x=FRAME_W / 2):
    half = 100
    return TrackedVehicle(
        track_id=track_id, class_id=2, confidence=0.9,
        x1=center_x - half, y1=300, x2=center_x + half, y2=500,
    )


def feed(det, vehicle, distance, start, seconds, hz=10):
    """Feed constant-distance samples; return first event or None."""
    event = None
    for i in range(int(seconds * hz)):
        e = det.update(vehicle, distance, now=start + i / hz)
        event = event or e
    return event


def test_sustained_close_vehicle_fires():
    det = TailgatingDetector(CFG, FRAME_W)
    assert feed(det, make_vehicle(), 5.0, 0.0, 4.0) is not None


def test_brief_close_pass_does_not_fire():
    det = TailgatingDetector(CFG, FRAME_W)
    assert feed(det, make_vehicle(), 5.0, 0.0, 1.5) is None


def test_far_vehicle_never_fires():
    det = TailgatingDetector(CFG, FRAME_W)
    assert feed(det, make_vehicle(), 25.0, 0.0, 10.0) is None


def test_adjacent_lane_filtered():
    det = TailgatingDetector(CFG, FRAME_W)
    side = make_vehicle(center_x=FRAME_W * 0.9)
    assert feed(det, side, 5.0, 0.0, 6.0) is None


def test_cooldown_suppresses_repeat():
    det = TailgatingDetector(CFG, FRAME_W)
    v = make_vehicle()
    assert feed(det, v, 5.0, 0.0, 4.0) is not None
    # Immediately after: still close, but inside cooldown.
    assert feed(det, v, 5.0, 4.0, 4.0) is None


def test_alert_reoccurs_after_cooldown():
    det = TailgatingDetector(CFG, FRAME_W)
    v = make_vehicle()
    assert feed(det, v, 5.0, 0.0, 4.0) is not None
    assert feed(det, v, 5.0, 30.0, 4.0) is not None


def test_missed_detections_tolerated():
    """A few high-distance blips (jitter) must not reset the timer."""
    det = TailgatingDetector(CFG, FRAME_W)
    v = make_vehicle()
    event = None
    hz = 10
    for i in range(50):
        d = 30.0 if i % 10 == 9 else 5.0  # 10% jitter frames
        e = det.update(v, d, now=i / hz)
        event = event or e
    assert event is not None
