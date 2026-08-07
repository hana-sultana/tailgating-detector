"""Camera capture abstraction.

Primary backend: Picamera2 (native CSI interface on Raspberry Pi OS).
Fallback backend: OpenCV VideoCapture (USB webcams, or development on a
laptop with a video file / webcam).

Both expose the same interface: .read() -> BGR ndarray | None, .release().
"""

from __future__ import annotations

import logging

import numpy as np

from config import CameraConfig

log = logging.getLogger(__name__)


class PiCamera:
    """Raspberry Pi Camera Module via Picamera2."""

    def __init__(self, cfg: CameraConfig):
        from picamera2 import Picamera2  # import here so dev machines don't need it

        self._cam = Picamera2()
        video_config = self._cam.create_video_configuration(
            main={"size": (cfg.width, cfg.height), "format": "RGB888"},
            controls={"FrameRate": cfg.fps},
        )
        self._cam.configure(video_config)
        self._cam.start()
        log.info("Picamera2 started at %dx%d@%dfps", cfg.width, cfg.height, cfg.fps)

    def read(self) -> np.ndarray | None:
        # Picamera2 RGB888 arrays are already BGR-ordered in memory for OpenCV.
        return self._cam.capture_array()

    def release(self) -> None:
        self._cam.stop()


class CvCamera:
    """OpenCV fallback: USB webcam index or a video file path for testing."""

    def __init__(self, cfg: CameraConfig, source: int | str | None = None):
        import cv2

        self._cap = cv2.VideoCapture(cfg.device_index if source is None else source)
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, cfg.width)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cfg.height)
        self._cap.set(cv2.CAP_PROP_FPS, cfg.fps)
        if not self._cap.isOpened():
            raise RuntimeError(f"Could not open video source: {source}")
        log.info("OpenCV capture opened (source=%s)", source)

    def read(self) -> np.ndarray | None:
        ok, frame = self._cap.read()
        return frame if ok else None

    def release(self) -> None:
        self._cap.release()


def create_camera(cfg: CameraConfig, source: int | str | None = None):
    """Return the best available camera backend.

    Pass source= a video file path to run the whole pipeline against
    recorded footage — the recommended way to develop off-vehicle.
    """
    if source is not None:
        return CvCamera(cfg, source)
    try:
        return PiCamera(cfg)
    except Exception as exc:  # noqa: BLE001 - fall back on any Picamera2 failure
        log.warning("Picamera2 unavailable (%s); falling back to OpenCV", exc)
        return CvCamera(cfg)
