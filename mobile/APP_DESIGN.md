# Companion Mobile App Design

## Phase 1: nRF Connect (zero code, week 5)

Scan → connect to **TailgateAlert** → expand the custom service → enable
notifications on the Alert characteristic (8e7c1a41-...). Each event
arrives as compact JSON. Good enough to demo the full pipeline.

## Phase 2: Custom app — Flutter (recommended over React Native)

Why Flutter: `flutter_blue_plus` is the most mature cross-platform BLE
library, background BLE behaves better than in the React Native BLE
ecosystem, and a single Dart codebase covers Android + iOS. React Native
is the better pick only if you already know React deeply — you don't
lose much either way, but BLE is the make-or-break dependency and
Flutter's story is stronger.

## Screens

```
┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│ HOME                 │  │ HISTORY              │  │ SETTINGS             │
│                      │  │                      │  │                      │
│   ● Connected        │  │ Today                │  │ Distance threshold   │
│   TailgateAlert      │  │ ├ 4:12p  6.4m  3.2s  │  │ [====|----] 8 m      │
│                      │  │ ├ 3:48p  7.1m  4.0s  │  │ Time threshold       │
│   Last alert:        │  │ Yesterday            │  │ [==|------] 3 s      │
│   6.4 m for 3.2 s    │  │ ├ 5:02p  5.9m  6.1s  │  │ Alert sound  [on]    │
│   2 min ago          │  │                      │  │ Vibrate      [on]    │
│                      │  │ (tap → event detail) │  │ Auto-reconnect [on]  │
│ [ Reconnect ]        │  │                      │  │                      │
└──────────────────────┘  └──────────────────────┘  └──────────────────────┘
```

- **Home**: connection state (scanning / connected / lost), last alert
  card, big reconnect button.
- **History**: local list of received events (JSON payloads persisted to
  SQLite), grouped by day.
- **Settings**: thresholds shown for reference (v1: read-only mirror of
  Pi config; v2: writable via a config BLE characteristic), sound/vibe
  toggles, auto-reconnect.

## Notification behavior

- Foreground: in-app banner + sound.
- Background: local push notification ("Vehicle following closely —
  6.4 m for 3.2 s") triggered from the BLE characteristic callback.
- Driving safety: default to sound/vibration; the driver should never
  need to look at the phone.

## Connection logic

```
start → scan(name=TailgateAlert, 10 s) → connect → discover service
      → subscribe(alert char) → listening
on disconnect → backoff scan loop (1 s, 2 s, 5 s, … cap 30 s) → reconnect
```

The Pi side needs no reconnection logic — as a peripheral it just keeps
advertising.
