# Sprint 1 review (SW-023)

Sprint 1 runs 12–25 October 2026. This note was written on 13 October, in the first week. It records the review and the retro from the work already on `main` and in open pull requests. The note can be edited again before the pull request is merged.

## Goal

Finish the first requirements and UML, show raw posture and distance on screen, and make sign-in possible on the server.

## Task status

| ID | Task | Owner | Status on 13 Oct |
| --- | --- | --- | --- |
| SW-011 | Requirements v1 | Ece + Buse | Merged |
| SW-012 | Use case diagram | Ece | Merged |
| SW-013 | Client class diagram | Ece | Merged |
| SW-014 | Server class diagram and ER diagram | Buse | Approved in open PR #11 on 7 Oct. Not merged |
| SW-015 | API specification v1 | Buse | Approved in open PR #11 on 7 Oct. Not merged |
| SW-016 | Architecture and ADR-001, ADR-002 | Ece + Buse | Merged |
| SW-017 | UI wireframes | Ece | Not started. Figma comes later |
| SW-018 | Neck and shoulder ratios on screen | Ece | Merged. Live on the camera card |
| SW-019 | Iris distance in centimetres | Ece | Code is on `feat/SW-019-iris-distance`. The card shows a centimetre value. Ruler check at 40/60/80 cm is still open, so there is no pull request yet |
| SW-020 | SQLAlchemy models and Alembic | Buse | Approved in open PR #11 on 7 Oct. Not merged |
| SW-021 | Sign-up, sign-in, JWT | Buse | Approved in open PR #12 on 13 Oct. Not merged |
| SW-022 | GitHub Actions lint and test | Buse | Approved in open PR #13 on 13 Oct. Not merged |
| SW-023 | This review | Ece + Buse | This file |
| SW-024 | Related apps and literature table | Buse | Not started |

Five of the fourteen planned tasks are on `main`: SW-011, SW-012, SW-013, SW-016, SW-018. Five more are approved and still open: SW-014, SW-015, and SW-020 in PR #11, SW-021 in PR #12, and SW-022 in PR #13. Approval does not merge them.

13 October is the second day of the sprint. The dates stay 12–25 October. The pace is about a week ahead of that two-week plan, because half the cards are already merged or approved.

## Review

The desktop app opens the camera and keeps frames in memory. The camera card shows resolution, frames per second, inference time, neck ratio, shoulder ratio, and platform. A straight sit reads a neck ratio near 0 and a shoulder tilt near 0. Distance is implemented locally and still needs the ruler before it is merged.

Shared documents in English now cover requirements, use cases, the client class diagram, the architecture diagram, and the two architecture decisions. The data contract is on `main`. Server sign-in, the database models, and CI are approved and waiting for Buse to merge. GitHub still marks PR #11, #12, and #13 as conflicted, so each branch needs an update before merge.

## Retro

What went well:

- One card stayed one branch and one pull request for the merged client and docs work.
- Posture numbers are visible without saving or sending an image.
- The neck metric uses a ratio, which matches the plan for a front camera.

What we will change:

- PR #11 holds SW-014, SW-015, and SW-020 together. Split those before merge so one card stays one branch.
- Update `main` before opening the next branch.

## Warnings

- **SW-017.** Figma wireframes are not started. Do not add a design link to the README until the frames exist.
- **SW-019.** Distance is on `feat/SW-019-iris-distance` and the card already shows centimetres. Do not open the pull request until a ruler check at 40, 60, and 80 cm. If 60 cm is off, change the camera field-of-view constant in `distance.ts` first.

## Sprint summary row

| Sprint | Planned | Done on main | Carried | What went well | What we will change |
| --- | --- | --- | --- | --- | --- |
| Sprint 1 | 14 | 5 merged; 5 approved and open | SW-017, SW-019, SW-024, plus #11–#13 until merged | About a week ahead on day 2; live posture on a local camera | Update conflicted branches before merge; ruler-check distance |
