"""Central configuration for the tailgating detection system.

Every tunable lives here so field calibration never requires touching
pipeline code. Values are grouped by subsystem.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CameraConfig:
    width: int = 1280
    height: int = 720
    fps: int = 30
    # Camera Module 3 wide: 102 deg horizontal FoV. Standard: 66 deg.
    horizontal_fov_deg: float = 66.0
    device_index: int = 0  # used only by the OpenCV fallback backend


@dataclass(frozen=True)
class DetectorConfig:
    # yolo26n = latest nano model (Jan 2026), NMS-free, fastest on Pi CPU.
    # Fallback to "yolo11n.pt" if your ultralytics version predates it.
    model_path: str = "yolo26n.pt"
    confidence_threshold: float = 0.4
    # COCO class ids: 2=car, 3=motorcycle, 5=bus, 7=truck
    vehicle_class_ids: tuple = (2, 3, 5, 7)
    # Inference size. 320 nearly doubles FPS vs 640 at some accuracy cost;
    # rear-view targets are large, so 320 is usually fine.
    imgsz: int = 320
    # Ultralytics built-in tracker config ("bytetrack.yaml" or "botsort.yaml")
    tracker: str = "bytetrack.yaml"


@dataclass(frozen=True)
class DistanceConfig:
    """Monocular distance estimation via the pinhole-camera model.

    distance_m = (real_height_m * focal_length_px) / bbox_height_px

    focal_length_px is derived from FoV and image width at runtime;
    override with a calibrated value for better accuracy (see
    docs/CALIBRATION.md).
    """
    assumed_vehicle_height_m: float = 1.5   # avg passenger car
    calibrated_focal_length_px: float | None = None
    # Exponential smoothing on per-track distance to damp bbox jitter.
    smoothing_alpha: float = 0.35


@dataclass(frozen=True)
class TailgatingConfig:
    # Distance below which a follower is "too close".
    distance_threshold_m: float = 8.0
    # Continuous seconds below threshold before an alert fires.
    time_threshold_s: float = 3.0
    # A track must exceed this lateral-center band to count as "behind us"
    # (fraction of frame width from center). Filters adjacent-lane cars.
    lane_center_band: float = 0.25
    # Cooldown between alerts for the same track id.
    alert_cooldown_s: float = 20.0
    # Fraction of frames within the window that must violate the threshold
    # (tolerates missed detections without resetting the timer).
    violation_ratio: float = 0.8


@dataclass(frozen=True)
class BleConfig:
    device_name: str = "TailgateAlert"
    # Custom 128-bit UUIDs (randomly generated for this project)
    service_uuid: str = "8e7c1a40-52ce-4f4e-b1f5-2f3d6a9c0e11"
    alert_char_uuid: str = "8e7c1a41-52ce-4f4e-b1f5-2f3d6a9c0e11"
    status_char_uuid: str = "8e7c1a42-52ce-4f4e-b1f5-2f3d6a9c0e11"


@dataclass(frozen=True)
class LoggingConfig:
    log_dir: str = "logs"
    log_level: str = "INFO"
    # Save annotated frames of alert events for later review/debugging.
    save_event_frames: bool = True
    event_frame_dir: str = "logs/events"


@dataclass(frozen=True)
class AppConfig:
    camera: CameraConfig = field(default_factory=CameraConfig)
    detector: DetectorConfig = field(default_factory=DetectorConfig)
    distance: DistanceConfig = field(default_factory=DistanceConfig)
    tailgating: TailgatingConfig = field(default_factory=TailgatingConfig)
    ble: BleConfig = field(default_factory=BleConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)


CONFIG = AppConfig()
