"""Vehicle detection and tracking.

Wraps Ultralytics YOLO's built-in track() call, which fuses detection
(YOLO26n) with multi-object tracking (ByteTrack). Using the built-in
tracker instead of a hand-rolled SORT gives persistent integer track IDs
across frames with one function call — the IDs are what let us measure
"how long has THIS vehicle been close".

Why these libraries:
- Ultralytics YOLO26n: current nano-scale model, NMS-free end-to-end
  inference, optimized for CPU/edge — the best accuracy-per-ms available
  on a Pi 5 without an accelerator.
- ByteTrack: strong association performance at negligible compute cost;
  ships inside ultralytics, zero extra dependencies.
- OpenCV: frame handling, drawing, video I/O.
- NumPy: array math shared by everything above.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np

from config import DetectorConfig

log = logging.getLogger(__name__)


@dataclass
class TrackedVehicle:
    track_id: int
    class_id: int
    confidence: float
    x1: float
    y1: float
    x2: float
    y2: float

    @property
    def bbox_height(self) -> float:
        return self.y2 - self.y1

    @property
    def center_x(self) -> float:
        return (self.x1 + self.x2) / 2.0


class VehicleDetector:
    def __init__(self, cfg: DetectorConfig):
        from ultralytics import YOLO

        self.cfg = cfg
        log.info("Loading model %s ...", cfg.model_path)
        self.model = YOLO(cfg.model_path)
        log.info("Model loaded.")

    def detect_and_track(self, frame: np.ndarray) -> list[TrackedVehicle]:
        """Run one frame through detection + tracking.

        persist=True keeps tracker state between calls so IDs are stable
        across the video stream.
        """
        results = self.model.track(
            frame,
            persist=True,
            conf=self.cfg.confidence_threshold,
            classes=list(self.cfg.vehicle_class_ids),
            imgsz=self.cfg.imgsz,
            tracker=self.cfg.tracker,
            verbose=False,
        )
        vehicles: list[TrackedVehicle] = []
        boxes = results[0].boxes
        if boxes is None or boxes.id is None:
            return vehicles

        ids = boxes.id.int().tolist()
        classes = boxes.cls.int().tolist()
        confs = boxes.conf.tolist()
        xyxy = boxes.xyxy.tolist()
        for tid, cid, conf, (x1, y1, x2, y2) in zip(ids, classes, confs, xyxy):
            vehicles.append(TrackedVehicle(tid, cid, conf, x1, y1, x2, y2))
        return vehicles
