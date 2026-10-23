# AGENTS.md — SitWise

This file contains shared rules for all AI agents (Cursor, Antigravity, etc.) and human contributors working on this repository. The agent reads this file in every task.

## Project

SitWise is a privacy-first desktop ergonomics assistant that monitors posture and eye strain using a standard webcam. It is a graduation project for Manisa Celal Bayar University, Computer Engineering (2 team members, October 2026 – January 2027).

## Folder structure

```
apps/desktop   Electron + React + Vite + TypeScript client (Track A)
apps/server    Python + FastAPI + PostgreSQL server (Track B)
docs/          vision.md, api/contract.md, adr/, uml/, meetings/
```

## Immutable rules

1. **Images are never saved or transmitted.** Camera frames are processed strictly in memory. Only numeric summaries reach the disk, logs, or server. Any PR violating this rule will not be merged.
2. **No CDN.** MediaPipe wasm and model files must be loaded locally from within the application package.
3. **Electron security:** `contextIsolation: true`, `nodeIntegration: false`, `sandbox: true`. The UI never accesses Node directly; new capabilities are exposed exclusively via narrow preload bridge functions.
4. **Agents touch only files relevant to the assigned card.** Do not reformat, rename, or "clean up" unrelated files.
5. **Keep PRs small:** One card = one branch = one PR.
6. **No secrets in the repository.** Passwords and secret keys reside in `.env`; the repository only tracks `.env.example`.

## Git and workflow

- Branch: `type/SW-id-short-name` (e.g., `feat/SW-024-blink-detector`). `main` is protected; no direct push.
- Commit: Conventional Commits, ending with the card ID. E.g., `feat(client): add EAR-based blink counter (SW-024)`.
- Scopes: `client`, `server`, `docs`, `ci`.
- PR description: What changed, how it was tested, and screenshots. Merged once the other team member approves.
- Major architectural decisions are documented as `docs/adr/ADR-00X-*.md`.

## Code style

- Formatting comes from repository configs; no manual debates:
  - Client: Prettier + ESLint (`npm run lint`, `npm run format`).
  - Server: black + flake8 (`apps/server/.flake8`, line length 88).
  - All: `.editorconfig`; line endings LF via `.gitattributes`; files UTF-8.
- TypeScript `strict`. Use proper types or `unknown` instead of `any`.
- Code, identifiers, and commit messages are in English; user-facing text and explanatory comments may be in Turkish.
- Measurement and analysis logic is written as pure TypeScript independent of React so that it can be tested easily.

## Definition of Done

A card moves to "Done" only when all of the following are met: PR merged into `main` with green CI · card acceptance criteria fulfilled · UML/tables updated if necessary · entry added to the Development Log.