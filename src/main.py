"""Entry point: capture -> detect/track -> distance -> decide -> alert.

Usage
-----
  python main.py                 # live camera (Pi)
  python main.py --video x.mp4   # run against recorded footage (dev)
  python main.py --show          # display annotated preview window

Runs entirely offline; BLE is the only radio used.
"""

from __future__ import annotations

import argparse
import logging
import signal
import time

from bluetooth import BleAlertServer
from camera import create_camera
from config import CONFIG
from detector import VehicleDetector
from distance_estimator import DistanceEstimator
from logger import save_event_frame, setup_logging
from tailgating_detector import TailgatingDetector

log = logging.getLogger("main")

_running = True


def _stop(*_):
    global _running
    _running = False


def main() -> None:
    parser = argparse.ArgumentParser(description="Tailgating detection system")
    parser.add_argument("--video", help="video file instead of live camera")
    parser.add_argument("--show", action="store_true", help="preview window")
    args = parser.parse_args()

    setup_logging(CONFIG.logging)
    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    camera = create_camera(CONFIG.camera, source=args.video)
    detector = VehicleDetector(CONFIG.detector)
    estimator = DistanceEstimator(CONFIG.distance, CONFIG.camera)
    decider = TailgatingDetector(CONFIG.tailgating, CONFIG.camera.width)
    ble = BleAlertServer(CONFIG.ble)
    ble.start()

    if args.show:
        import cv2

    frames, t0 = 0, time.monotonic()
    log.info("Pipeline running. Ctrl+C to stop.")
    try:
        while _running:
            frame = camera.read()
            if frame is None:
                log.info("End of stream.")
                break

            vehicles = detector.detect_and_track(frame)
            active = {v.track_id for v in vehicles}

            for v in vehicles:
                d = estimator.estimate(v)
                event = decider.update(v, d)
                if event:
                    log.warning(
                        "TAILGATING: id=%d dist=%.1fm dur=%.1fs",
                        event.track_id, event.distance_m, event.duration_s,
                    )
                    ble.send_alert(event)
                    save_event_frame(CONFIG.logging, frame, v, event)

            estimator.forget(active)
            decider.prune(active)

            frames += 1
            if frames % 100 == 0:
                fps = frames / (time.monotonic() - t0)
                log.info("throughput: %.1f FPS", fps)

            if args.show:
                for v in vehicles:
                    cv2.rectangle(
                        frame,
                        (int(v.x1), int(v.y1)),
                        (int(v.x2), int(v.y2)),
                        (0, 255, 0), 2,
                    )
                cv2.imshow("tailgate", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
    finally:
        camera.release()
        log.info("Shut down cleanly.")


if __name__ == "__main__":
    main()
