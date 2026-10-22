# ADR-002: Process camera images only on the user's computer

- **Status:** Accepted
- **Date:** 2026-10-06
- **Card:** SW-016
- **Requirement:** NFR-01 (privacy)

## Problem

SitWise uses the webcam all day. A camera image shows the user's face, room and screen, so it is very sensitive data. Users will not trust an app that sends this to a server. On the other hand, the server needs data to show daily scores, history and to learn personal thresholds.

## Decision

All image processing happens **on the user's computer**. MediaPipe runs inside the Electron client. Frames are only kept in memory; they are never written to disk and never sent to the server. The client sends only the numeric summaries defined in `docs/api/contract.md`: metric samples, alerts and feedback.

## Alternatives we did not choose

| Option | Why not |
|--------|---------|
| Send frames or video to the server and process them there | Breaks user privacy, needs a lot of bandwidth, and the server would need a GPU. |
| Save short video clips on the computer for later review | Still creates sensitive files on disk that could leak; not needed for our features. |

## Result

- Privacy rule NFR-01: no image leaves the computer and no image is saved.
- Less network traffic: one small JSON summary every 10 seconds.
- The app keeps working without internet; summaries wait in a queue (NFR-03).
- Cost: analysis uses the user's CPU, so we must keep it light (NFR-02).
- How we check it: code review and a network traffic check during testing (TC-10).
