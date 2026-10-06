# ADR-001: Build the client as an Electron desktop app

- **Status:** Accepted
- **Date:** 2026-10-06
- **Card:** SW-016

## Problem

SitWise must watch the user's posture during the whole working day, not only while its window is open. It needs a tray icon, it must keep the camera running when the window is closed, and it must start when the computer starts. The team knows web technologies (React, TypeScript) and MediaPipe has a good web version.

## Decision

We build the client with **Electron + React + Vite + TypeScript**. Electron packages the web app as a desktop app for Windows (and optionally macOS).

## Alternatives we did not choose

| Option | Why not |
|--------|---------|
| Web app in a browser tab | Browsers slow down or stop background tabs, so tracking is not reliable. A tab cannot show a tray icon or start with the computer. Closing the tab stops tracking. |
| Mobile app | The user works at a desk in front of a computer screen. The phone camera is not in the right place to see posture and screen distance. |
| Native desktop app (C#, Qt, Swift) | The team would have to learn a new UI stack. It would be harder to support Windows and macOS with the same code. |

## Result

- We get a tray icon, background work and auto start (SW-007).
- We keep using React and the web version of MediaPipe.
- One codebase for Windows and macOS; a Windows installer is planned (SW-063).
- Cost: Electron apps use more memory than native apps. We will measure CPU use and keep it under the target in NFR-02 (below 15 %).
