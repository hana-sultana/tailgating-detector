"""BLE alert transmission.

Design
------
The Pi advertises as a BLE *peripheral* named "TailgateAlert" exposing a
custom GATT service:

  Service  8e7c1a40-...   Tailgate Alert Service
    Char   8e7c1a41-...   Alert     (read, notify)  JSON event payload
    Char   8e7c1a42-...   Status    (read)          "OK" heartbeat

The phone (central) connects and subscribes to the Alert characteristic.
When a tailgating event fires, we update the characteristic value, which
pushes a BLE notification to every subscribed phone. Prototype with the
free nRF Connect app: scan -> connect to TailgateAlert -> enable notify
on the Alert characteristic.

Implementation uses `bluezero` (a friendly wrapper over BlueZ D-Bus).
Reconnection is inherent to the peripheral model: we just keep
advertising; if the phone drops, it re-subscribes when it reconnects.

Payload format (JSON, <= 180 bytes to fit comfortably in one MTU after
negotiation; falls back to truncation on tiny default MTUs):
  {"t": 1722500000, "id": 12, "d": 6.4, "s": 3.2}
   t=unix time, id=track id, d=distance m, s=duration s
"""

from __future__ import annotations

import json
import logging
import threading

from config import BleConfig
from tailgating_detector import TailgatingEvent

log = logging.getLogger(__name__)


class BleAlertServer:
    def __init__(self, cfg: BleConfig):
        self.cfg = cfg
        self._peripheral = None
        self._thread: threading.Thread | None = None
        self._latest_payload = b"{}"

    # ---- characteristic callbacks -------------------------------------
    def _read_alert(self) -> list[int]:
        return list(self._latest_payload)

    def _read_status(self) -> list[int]:
        return list(b"OK")

    # ---- lifecycle ----------------------------------------------------
    def start(self) -> None:
        """Start advertising in a background thread. Never raises on
        missing Bluetooth hardware — logs and degrades to a no-op so the
        vision pipeline still runs during development."""
        try:
            from bluezero import adapter, peripheral
        except ImportError:
            log.warning("bluezero not installed; BLE disabled")
            return

        try:
            addr = list(adapter.Adapter.available())[0].address
        except (IndexError, Exception) as exc:  # noqa: BLE001
            log.warning("No BLE adapter available (%s); BLE disabled", exc)
            return

        p = peripheral.Peripheral(addr, local_name=self.cfg.device_name)
        p.add_service(srv_id=1, uuid=self.cfg.service_uuid, primary=True)
        p.add_characteristic(
            srv_id=1, chr_id=1, uuid=self.cfg.alert_char_uuid,
            value=[], notifying=False,
            flags=["read", "notify"],
            read_callback=self._read_alert,
        )
        p.add_characteristic(
            srv_id=1, chr_id=2, uuid=self.cfg.status_char_uuid,
            value=[], notifying=False,
            flags=["read"],
            read_callback=self._read_status,
        )
        self._peripheral = p
        self._thread = threading.Thread(target=p.publish, daemon=True)
        self._thread.start()
        log.info("BLE advertising as '%s'", self.cfg.device_name)

    def send_alert(self, event: TailgatingEvent) -> None:
        payload = json.dumps(
            {
                "t": int(event.timestamp),
                "id": event.track_id,
                "d": round(event.distance_m, 1),
                "s": round(event.duration_s, 1),
            }
        ).encode()
        self._latest_payload = payload
        if self._peripheral is None:
            log.info("[BLE disabled] alert: %s", payload.decode())
            return
        try:
            # Updating a notifying characteristic pushes to subscribers.
            char = self._peripheral.characteristics[0]
            char.set_value(list(payload))
            log.info("BLE alert sent: %s", payload.decode())
        except Exception as exc:  # noqa: BLE001
            log.error("BLE notify failed: %s", exc)
