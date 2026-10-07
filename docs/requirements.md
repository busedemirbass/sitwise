# Requirements v1 (SW-011)

This document is section 4.1 of the roadmap, kept in the repo. It lists what SitWise must do. It does not describe how the code is written.

Two people share this file. Client rows are Ece's. Server rows are Buse's. The tables themselves stay one list, so the report and the tasks use the same sentences.

## Functional requirements

Priority uses MoSCoW: Must (required for delivery), Should (sets the project apart), Could (only if time remains).

| ID | Requirement | Priority | Task |
| --- | --- | --- | --- |
| FR-01 | The app runs in the background, shows a tray icon, and starts when the computer starts | Must | SW-007 |
| FR-02 | The user completes a 5-second personal calibration; a bad calibration is rejected | Must | SW-027 |
| FR-03 | The system tracks forward head posture and shoulder balance | Must | SW-018 |
| FR-04 | The system estimates distance to the screen in centimeters | Must | SW-019 |
| FR-05 | The system measures blinks per minute | Must | SW-026 |
| FR-06 | A gentle notification is sent when poor posture persists | Must | SW-035 |
| FR-07 | The user can mark an alert as wrong | Must | SW-036, SW-037 |
| FR-08 | The user can create an account and sign in | Must | SW-021 |
| FR-09 | The dashboard shows the daily score and an hour-by-hour colored timeline | Must | SW-038, SW-039 |
| FR-10 | Calendar history and an end-of-day fatigue question scored from 1 to 5 | Should | SW-044, SW-045 |
| FR-11 | The threshold learns from alerts the user marks as wrong | Should | SW-046 |
| FR-12 | The system gives a concrete desk-setup suggestion | Should | SW-047 |
| FR-13 | A mini indicator stays above other windows | Should | SW-048 |
| FR-14 | A gradual fatigue score is computed from posture and blink data | Should | SW-053 |
| FR-15 | A smart break suggestion, with a classic Pomodoro option | Should | SW-054, SW-055 |
| FR-16 | A weekly summary email | Could | SW-090 |

Client rows: FR-01, FR-02, FR-03, FR-04, FR-05, FR-06, FR-09, FR-12, FR-13. FR-07 is shared: the button is SW-036 (client), the saved record is SW-037 (server). FR-15 is shared: the screen is client, the break rule is server.

Server rows: FR-08, FR-10, FR-11, FR-14, FR-16.

## Non-functional requirements

| ID | Category | Requirement | How it is checked |
| --- | --- | --- | --- |
| NFR-01 | Privacy | Camera frames are not written to disk and are not sent to the server; only numeric summaries are sent | Code review and a network-traffic check (TC-10) |
| NFR-02 | Performance | Average CPU use while tracking stays under 15% | A 30-minute measurement in the task manager (TC-09) |
| NFR-03 | Reliability | If the network drops, data waits in a queue and is not lost | TC-07 |
| NFR-04 | Security | Passwords are hashed (bcrypt or argon2) and the API is protected with JWT | TC-06 |
| NFR-05 | Usability | The average SUS questionnaire score is above 70 | SW-062 |
| NFR-06 | Portability | The app runs on Windows 10 and 11; macOS is optional | SW-063 |
| NFR-07 | Maintainability | The server service layer has at least 70% test coverage | CI report |

Client checks: NFR-01, NFR-02, NFR-06. Server checks: NFR-03, NFR-04, NFR-07. NFR-05 is shared; the questionnaire is filled during the volunteer test.
