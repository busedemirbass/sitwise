# Screen wireframes (SW-017)

These files are the visual reference for the desktop screens. They are not the SitWise application. Do not copy them into `apps/desktop`. Later cards rebuild each screen in React, using the colours, spacing, and layout shown here.

## What is here

| File | Screen |
| --- | --- |
| `Dashboard.dc.html` | Dashboard (SW-039) |
| `Calibration.dc.html` | Calibration (SW-027) |
| `RecordingSetup.dc.html` | Recording, before start (SW-072) |
| `RecordingSession.dc.html` | Recording, during the session (SW-072) |
| `RecordingSaved.dc.html` | Recording, session saved (SW-072) |
| `Settings.dc.html` | Settings (SW-055) |
| `MiniIndicator.dc.html` | Mini indicator (SW-048) |
| `Main.dc.html` | Dikdik mascot sheet |

`support.js` and `vendor/` only draw these pages in a browser. They are not application code.

The pages link to each other by file name. They stay in this folder, next to `support.js` and `vendor/`. Moving one file breaks the menu.

## How to open

From the repository root:

```bash
cd docs/design
python3 -m http.server 8765
```

Then open <http://127.0.0.1:8765/Dashboard.dc.html>. Opening an HTML file directly can block the scripts.

Nunito and Caveat load from Google Fonts when these pages are viewed. That link stays in the reference only. The Electron app does not use it.

## What a later card does

Look at the page, then build the screen in `apps/desktop` with the project's own components. Leave these files unchanged.
