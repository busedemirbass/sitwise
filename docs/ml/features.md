# Feature definitions (SW-071)

This file lists the numbers computed from MediaPipe landmarks. Names match the code. A formula that is not in the code is not filled in.

## Where the code computes a metric

| Name | What it measures | File | On `main` |
| --- | --- | --- | --- |
| `neckRatio` | Horizontal offset of the nose from the shoulder midpoint, divided by shoulder width | `apps/desktop/src/renderer/src/posture.ts` | Yes |
| `shoulderTilt` | Shoulder height difference, divided by the same width | `apps/desktop/src/renderer/src/posture.ts` | Yes |
| `distanceCm` | Screen distance from the iris diameter | `apps/desktop/src/renderer/src/distance.ts` | No. The file is on `feat/SW-019-iris-distance` (PR #15) |

`useMediaPipe.ts` calls these functions. It does not contain a second formula. No file computes EAR.

Pose points are nose 0, left shoulder 11, right shoulder 12. A pose point is used when `visibility` is missing or at least 0.5. Image x and y are 0–1. y grows downward.

## Metrics in the code

| Name | Measures | Landmarks | Formula | Unit | Calibration | File |
| --- | --- | --- | --- | --- | --- | --- |
| `neckRatio` | How far the nose sits sideways from the middle of the shoulders | Pose 0, 11, 12 | `shoulderWidth = hypot(left.x - right.x, left.y - right.y)`. `midX = (left.x + right.x) / 2`. `neckRatio = abs(nose.x - midX) / shoulderWidth` | Ratio, no unit. 0 means centred | Not normalized by a personal baseline | `posture.ts` |
| `shoulderTilt` | Which shoulder is lower | Pose 11, 12 | `shoulderTilt = (left.y - right.y) / shoulderWidth`. The sign follows the camera image, not the mirrored preview | Signed ratio, no unit. Near 0 means level | Not normalized by a personal baseline | `posture.ts` |
| `distanceCm` | Distance from the face to the camera | Face iris edges: left 471 and 469, right 476 and 474 | Each eye diameter is the pixel distance between its two edge points. Diameters under 2 px are dropped. `irisPx` is the mean of the eyes that remain. `focalPx = (videoWidth / 2) / tan(30°)`, from a 60° horizontal field of view. `distanceCm = (11.7 * focalPx) / irisPx / 10` | cm | Not normalized by a personal baseline. 11.7 mm is a fixed adult iris size | `distance.ts` on the SW-019 branch |

If both irises are missing, or the video is smaller than 2 px, `distanceCm` is null. If the shoulders are closer than `0.0001` in normalized units, both posture values are null.

## Planned

These are not computed anywhere in the client. The formulas below are the usual published definitions. Landmark indices for this project are kontrol edilecek.

| Name | Measures | Formula | Unit | Status |
| --- | --- | --- | --- | --- |
| EAR | How closed one eye is | Soukupová and Čech: `(||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)`, with six points around the eye. Which MediaPipe indices are p1–p6: kontrol edilecek | Ratio, no unit | Not in the code |
| Blinks per minute | Blink events in one minute | A blink is an EAR drop below a threshold and a rise back above it. Count those events over 60 seconds. The threshold: kontrol edilecek | blinks/min | Not in the code |
| PERCLOS | Fraction of a time window spent with the eyes closed | `(closed frames / frames in the window)`. The rule that marks a frame closed: kontrol edilecek | Ratio from 0 to 1, often written as a percent | Not in the code |
| MAR | Mouth opening, used as a yawn cue | Vertical mouth opening divided by horizontal mouth width. The MediaPipe mouth indices: kontrol edilecek | Ratio, no unit | Not in the code |
| Head drop | Forward drop of the head | No formula is selected. A pitch angle from the nose and the eyes is a common choice. The exact expression: kontrol edilecek | kontrol edilecek | Not in the code |

## Normalization

Shoulder width is in the code. For `neckRatio` and `shoulderTilt`, the raw pixel-free offset is divided by `shoulderWidth`. A person who sits closer has a wider shoulder span in the image, and the division keeps the ratio comparable. `distanceCm` does not use shoulder width. It uses the iris size and the camera field of view.

A difference from the upright calibration value is not in the code. Nothing stores the 5-second upright sit, and no metric subtracts that baseline. That step is SW-027. Until then the live number is the number in the table above.
