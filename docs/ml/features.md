# Feature definitions (SW-071)

This file lists the numbers computed from MediaPipe landmarks. Names match the code. Planned formulas are the published definitions, marked as not implemented.

## Where the code computes a metric

| Name | What it measures | File | On `main` |
| --- | --- | --- | --- |
| `neckRatio` | Horizontal (sideways) offset of the nose from the shoulder midpoint, divided by shoulder width. The name is misleading: it does not measure forward lean or a slouch | `apps/desktop/src/renderer/src/posture.ts` | Yes |
| `shoulderTilt` | Shoulder height difference, divided by the same width | `apps/desktop/src/renderer/src/posture.ts` | Yes |
| `distanceCm` | Screen distance from the iris diameter | `apps/desktop/src/renderer/src/distance.ts` | No. The file is on `feat/SW-019-iris-distance` (PR #15) |

`useMediaPipe.ts` calls these functions. It does not contain a second formula. No file computes EAR.

Pose points are nose 0, left shoulder 11, right shoulder 12. A pose point is used when `visibility` is missing or at least 0.5. Image x and y are 0–1. y grows downward.

## Metrics in the code

| Name | Measures | Landmarks | Formula | Unit | Calibration | File |
| --- | --- | --- | --- | --- | --- | --- |
| `neckRatio` | How far the nose sits sideways from the middle of the shoulders. The name is misleading: it measures horizontal (sideways) shift of the head, not forward lean or a slouch. The code name stays `neckRatio` | Pose 0, 11, 12 | `shoulderWidth = hypot(left.x - right.x, left.y - right.y)`. `midX = (left.x + right.x) / 2`. `neckRatio = abs(nose.x - midX) / shoulderWidth` | Ratio, no unit. 0 means centred | Not normalized by a personal baseline | `posture.ts` |
| `shoulderTilt` | Which shoulder is lower | Pose 11, 12 | `shoulderTilt = (left.y - right.y) / shoulderWidth`. The sign follows the camera image, not the mirrored preview | Signed ratio, no unit. Near 0 means level | Not normalized by a personal baseline | `posture.ts` |
| `distanceCm` | Distance from the face to the camera | Face iris edges: left 471 and 469, right 476 and 474 | Each eye diameter is the pixel distance between its two edge points. Diameters under 2 px are dropped. `irisPx` is the mean of the eyes that remain. `focalPx = (videoWidth / 2) / tan(30°)`, from a 60° horizontal field of view. `distanceCm = (11.7 * focalPx) / irisPx / 10` | cm | Not normalized by a personal baseline. 11.7 mm is a fixed adult iris size | `distance.ts` on the SW-019 branch |

If both irises are missing, or the video is smaller than 2 px, `distanceCm` is null. If the shoulders are closer than `0.0001` in normalized units, both posture values are null.

## Planned

These are not computed anywhere in the client. Where a published definition is used, the cell says so: literature standard, to be checked visually. The slouch rows are the SW-018 v2 additions.

| Name | Measures | Formula | Unit | Status |
| --- | --- | --- | --- | --- |
| `noseShoulderDrop` | How far the nose has dropped toward the shoulders. It gets smaller in a slouch, because y grows downward | Pose 0, 11, 12. `(shoulderMidY - nose.y) / shoulderWidth`, with `shoulderMidY = (left.y + right.y) / 2` | Ratio, no unit | Not in the code. SW-018 v2 |
| `earShoulderDrop` | Neck shortening. Mean of the two sides | Pose 7 (left ear), 8 (right ear), 11, 12. Mean of `(leftShoulder.y - leftEar.y) / shoulderWidth` and `(rightShoulder.y - rightEar.y) / shoulderWidth` | Ratio, no unit | Not in the code. SW-018 v2 |
| `headPitch` | Up-down angle of the head | Pitch, in degrees, taken from the FaceLandmarker facial transformation matrix | degrees | Not in the code. SW-018 v2 |
| EAR | How closed one eye is | Soukupová and Čech, 2016: `(\|p2−p6\| + \|p3−p5\|) / (2·\|p1−p4\|)`. Face Mesh indices, literature standard, to be checked visually: left eye 33, 160, 158, 133, 153, 144; right eye 362, 385, 387, 263, 373, 380. No fixed threshold is written down. Calibration sets it. The literature value is about 0.2 | Ratio, no unit | Not in the code |
| Blinks per minute | Blink events in one minute | A blink is an EAR drop below the calibration threshold and a rise back above it. Count those events over 60 seconds. The threshold is not fixed. Calibration sets it. The literature value is about 0.2 | blinks/min | Not in the code |
| PERCLOS | Share of a minute spent with the eye mostly closed | Over a 60-second window, the fraction of time the eye is more than 80% closed (P80). Literature standard, to be checked visually | Ratio from 0 to 1 | Not in the code |
| MAR | Mouth opening, used as a yawn cue | Inner vertical mouth opening divided by mouth width. Indices, literature standard, to be checked visually: 13 and 14 for the vertical pair, 78 and 308 for the horizontal pair | Ratio, no unit | Not in the code |
| Head drop | A sudden forward drop of the head | A short, sharp fall in `noseShoulderDrop`. The threshold will be set by experiment | Same ratio as `noseShoulderDrop` | Not in the code |

## Normalization

Shoulder width is in the code. For `neckRatio` and `shoulderTilt`, the raw pixel-free offset is divided by `shoulderWidth`. A person who sits closer has a wider shoulder span in the image, and the division keeps the ratio comparable. `distanceCm` does not use shoulder width. It uses the iris size and the camera field of view.

A difference from the upright calibration value is not in the code. Nothing stores the 5-second upright sit, and no metric subtracts that baseline. That step is SW-027. Until then the live number is the number in the table above.
