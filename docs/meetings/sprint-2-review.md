# Sprint 2 review (SW-034)

Sprint 2 ran 26 October–8 November 2026. This note was written on 26 November, after that window. It records what is on `main` and what is still an open pull request. Approval does not merge a pull request.

## Goal

Calibration and blink counting work. The camera-to-feature-to-server chain closes. Recording mode writes the first numeric sessions, and the training pipe can run on those sessions.

## Task status

| ID | Task | Owner | Status on 26 Nov |
| --- | --- | --- | --- |
| SW-025 | One feature call for posture and distance | Ece | Merged, PR #28 |
| SW-026 | Blink count from the eye aspect ratio | Ece | Merged, PR #32 |
| SW-027 | Five-second upright calibration; a slouch is rejected | Ece | Merged, PR #33 |
| SW-028 | Metric queue until the server accepts the rows | Ece | Open PR #36. Review still required |
| SW-029 | `/sessions`, `/metrics`, `/calibration` | Buse | Merged before the sprint window |
| SW-030 | Repository and service tests | Buse | Approved in open PR #29. Not merged |
| SW-031 | Fake data generator | Buse | Approved in open PR #30. Not merged |
| SW-072 | Recording mode, one numeric CSV, no image | Ece | Merged, PR #34 |
| SW-073 | Eyeblink8 and MultiPosture pipeline | Buse | Approved in open PR #31. Not merged |
| SW-074 | Two-person pilot and protocol note | Ece + Buse | Open PR #35. Review still required |
| SW-084 | `ml/` skeleton and a logged posture run | Ece | Open PR #37. Review still required |
| SW-032 | Milestone M1, live data-pipeline demo on 8 November | Ece + Buse | No demo note was written |
| SW-034 | This review | Ece + Buse | This file |

Five of the thirteen planned tasks are on `main`: SW-025, SW-026, SW-027, SW-029, and SW-072. Three more are approved and still open: SW-030 in PR #29, SW-031 in PR #30, and SW-073 in PR #31. Three are waiting for a review: SW-028 in PR #36, SW-074 in PR #35, and SW-084 in PR #37.

## Review

The desktop app calibrates an upright sit, rejects a slouch, counts blinks per minute, and writes one protocol session as a numeric CSV. Camera frames stay in memory.

PR #36 keeps a 10-second numeric row in a queue until `POST /metrics` accepts it. A dropped network leaves the row in that queue. The row carries the measured blink count from SW-026. The reviewer still has to cut the network, restore it, and see the same rows arrive.

PR #35 records the two teammate sittings. `P01` was checked on disk on 27 October: 2274 rows, ruler values 40, 60, and 80 only on the distance step, and no image. `P02` stays on the other computer. The protocol text did not change after those sittings. Neither CSV is in the repository.

PR #37 loads those CSVs from a folder outside the repository, splits by person, and appends the score to `ml/results/posture.csv`. The logged run uses P01 and P02. With two people the score only shows that the pipe runs. The logistic regression, random forest, and LightGBM comparison stays on SW-076.

The 8 November live demo has no written record.

## Retro

What went well:

- Calibration, blink counting, and the protocol CSV each landed as one branch and one pull request.
- The pilot CSVs and the training log contain numbers only.
- Buse's server, fake-data, and public-data cards were approved in the sprint window.

What we will change:

- Merge an approved pull request in the same week. PR #29, #30, and #31 have been approved since 27 October.
- Write the milestone demo in this file when it happens, on the day it happens.

## Sprint summary row

| Sprint | Planned | Done on main | Carried | What went well | What we will change |
| --- | --- | --- | --- | --- | --- |
| Sprint 2 | 13 | 5 merged | SW-028, SW-030, SW-031, SW-032, SW-073, SW-074, SW-084, and this note until merged | Calibration, blinks, and one numeric CSV on `main` | Merge approved pull requests in the same week |
