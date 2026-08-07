"""Logging: rotating text logs + annotated snapshot frames of each event.

Event frames are the project's evidence trail — each alert saves one
annotated JPEG so you can audit false positives after a drive.
"""

from __future__ import annotations

import logging
import logging.handlers
import time
from pathlib import Path

import numpy as np

from config import LoggingConfig
from detector import TrackedVehicle
from tailgating_detector import TailgatingEvent


def setup_logging(cfg: LoggingConfig) -> None:
    Path(cfg.log_dir).mkdir(parents=True, exist_ok=True)
    Path(cfg.event_frame_dir).mkdir(parents=True, exist_ok=True)

    handler = logging.handlers.RotatingFileHandler(
        Path(cfg.log_dir) / "tailgate.log", maxBytes=2_000_000, backupCount=5
    )
    console = logging.StreamHandler()
    logging.basicConfig(
        level=getattr(logging, cfg.log_level),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[handler, console],
    )


def save_event_frame(
    cfg: LoggingConfig,
    frame: np.ndarray,
    vehicle: TrackedVehicle,
    event: TailgatingEvent,
) -> Path | None:
    if not cfg.save_event_frames:
        return None
    import cv2

    annotated = frame.copy()
    p1 = (int(vehicle.x1), int(vehicle.y1))
    p2 = (int(vehicle.x2), int(vehicle.y2))
    cv2.rectangle(annotated, p1, p2, (0, 0, 255), 2)
    label = f"id={event.track_id} {event.distance_m:.1f}m {event.duration_s:.1f}s"
    cv2.putText(
        annotated, label, (p1[0], max(p1[1] - 8, 16)),
        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2,
    )
    out = Path(cfg.event_frame_dir) / f"event_{int(time.time())}_{event.track_id}.jpg"
    cv2.imwrite(str(out), annotated)
    return out
