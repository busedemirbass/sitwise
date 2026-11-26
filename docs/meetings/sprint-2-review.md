# Sprint 2 review (SW-034)

Sprint 2 ran 26 October–8 November 2026. This note was updated on 26 November, after Buse merged the remaining client and training pull requests. The teammates confirmed that the M1 demo was shown to the advisor.

## Goal

Calibration and blink counting work. The camera-to-feature-to-server chain closes. Recording mode writes the first numeric sessions, and the training pipe can run on those sessions.

## Task status

| ID | Task | Owner | Status on 26 Nov |
| --- | --- | --- | --- |
| SW-025 | One feature call for posture and distance | Ece | Merged, PR #28 |
| SW-026 | Blink count from the eye aspect ratio | Ece | Merged, PR #32 |
| SW-027 | Five-second upright calibration; a slouch is rejected | Ece | Merged, PR #33 |
| SW-028 | Metric queue until the server accepts the rows | Ece | Merged, PR #36 |
| SW-029 | `/sessions`, `/metrics`, `/calibration` | Buse | Merged before the sprint window |
| SW-030 | Repository and service tests | Buse | Approved in open PR #29. Not merged |
| SW-031 | Fake data generator | Buse | Approved in open PR #30. Not merged. This branch also contains the SW-030 commit |
| SW-072 | Recording mode, one numeric CSV, no image | Ece | Merged, PR #34 |
| SW-073 | Eyeblink8 and MultiPosture pipeline | Buse | Approved in open PR #31. Not merged |
| SW-074 | Two-person pilot and protocol note | Ece + Buse | Merged, PR #35 |
| SW-084 | `ml/` skeleton and a logged posture run | Ece | Merged, PR #37 |
| SW-032 | Milestone M1, data-pipeline demo | Ece + Buse | Shown to the advisor |
| SW-034 | This review | Ece + Buse | This file |

Eight of the thirteen planned tasks are on `main`: SW-025, SW-026, SW-027, SW-028, SW-029, SW-072, SW-074, and SW-084. The M1 demo was shown. Three approved pull requests are still open: SW-030 in PR #29, SW-031 in PR #30, and SW-073 in PR #31. Each of those three merges cleanly onto current `main`.

## Review

The desktop app calibrates an upright sit, rejects a slouch, counts blinks per minute, and writes one protocol session as a numeric CSV. Camera frames stay in memory. A 10-second numeric row stays in a queue until `POST /metrics` accepts it.

The two teammate sittings are recorded in the protocol note. `P01` was checked on disk on 27 October: 2274 rows, ruler values 40, 60, and 80 only on the distance step, and no image. `P02` stays on the other computer. Neither CSV is in the repository. `python -m ml.train posture` has already logged a leave-one-subject run for those two people in `ml/results/posture.csv`.

The teammates showed this chain to the advisor: live features, calibration, blinks, one numeric recording, and the path from those numbers toward the server and the training script.

## Retro

What went well:

- Calibration, blink counting, the protocol CSV, the metric queue, and the training skeleton each landed as one branch and one pull request.
- The pilot CSVs and the training log contain numbers only.
- The M1 demo reached the advisor.

What we will change:

- Merge an approved pull request in the same week. PR #29, #30, and #31 have been approved since 27 October and still sit outside `main`.

## Sprint summary row

| Sprint | Planned | Done on main | Carried | What went well | What we will change |
| --- | --- | --- | --- | --- | --- |
| Sprint 2 | 13 | 8 merged; M1 shown | SW-030, SW-031, SW-073, and this note until merged | Live chain shown to the advisor | Merge the three approved server and pipeline pull requests |
