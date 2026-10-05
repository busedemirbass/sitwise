# Data contract v0 (SW-010)

Three messages the client sends to the server. No image is sent, only these numbers.

## 1. Metric sample

A 10-second posture summary. `session_id` comes from the server.

```json
{
  "session_id": "6f1c0a2e-3b4d-4e5f-8a9b-0c1d2e3f4a5b",
  "samples": [
    {
      "ts": "2026-10-05T08:34:00Z",
      "neck_ratio": 0.42,
      "shoulder_tilt": 0.03,
      "distance_cm": 58.0,
      "blinks_per_min": 16,
      "state": "ok"
    }
  ]
}
```

| Field | Meaning | Unit |
| --- | --- | --- |
| ts | Measurement time | ISO timestamp |
| neck_ratio | Forward head posture | ratio |
| shoulder_tilt | Shoulder balance | ratio |
| distance_cm | Distance to the screen | cm |
| blinks_per_min | Blinks per minute | count |
| state | `ok` or `warn` | — |

A field that is not measured yet may be `null`.

## 2. Alert

Sent when poor posture or a low blink rate persists.

```json
{
  "session_id": "6f1c0a2e-3b4d-4e5f-8a9b-0c1d2e3f4a5b",
  "ts": "2026-10-05T08:34:10Z",
  "type": "neck",
  "severity": "warn"
}
```

`type`: `neck`, `shoulder`, `distance`, `blink`. `severity`: `info`, `warn`.

## 3. Feedback

Sent when the user marks an alert as wrong. `alert_id` comes from the server.

```json
{
  "alert_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "is_false": true
}
```

## Server mapping

Filled in by the server owner: the endpoint for each JSON, the matching table, and the status code returned for an invalid request.
