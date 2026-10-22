# ADR-003: Train models on landmark numbers, not on images

- **Status:** Accepted
- **Date:** 2026-10-21
- **Card:** SW-016
- **Requirement:** NFR-01 (privacy), FR-18

## Problem

SitWise has to classify posture, estimate screen distance and score fatigue. A fixed threshold is simple, but it does not adapt to a person. A neural net trained on camera images would need many face videos, and those videos are exactly the data we promised not to store. The model also has to run all day on a normal laptop.

## Decision

Models learn from numbers computed on MediaPipe landmarks: neck and shoulder measures, iris size, eye aspect ratio, and the same kind of values over a short window. They do not learn from pixels. The chosen model is exported to ONNX and runs inside the Electron client with ONNX Runtime. The server still receives only the numeric summaries from ADR-002.

The rule-based thresholds stay in the product as the baseline. The report compares four approaches on the same unseen people: those thresholds, a model trained only on public data, a model trained on SitWise-Desk, and a personalized threshold.

## Alternatives we did not choose

| Option | Why not |
|--------|---------|
| Train a convolutional network on face or body images | Needs stored video, conflicts with NFR-01, and is out of scope. |
| Use only a fixed threshold, with no trained model | Stays as the baseline we compare against. It is not the only method in the final report. |
| Run the trained model on the server | The features would be enough, but the decision itself should stay on the computer next to the camera, and the laptop must keep working offline. |

## Result

- SitWise-Desk stores rows of numbers and labels. It stores no image.
- Public videos are converted to the same feature columns, then the video file is not kept in the repo.
- A small table of features is enough to train logistic regression, a random forest or LightGBM.
- Cost: the feature formulas have to be written once and shared by the client and the training script. That list is SW-071.
- If ONNX integration slips, the logistic-regression coefficients can be copied into TypeScript. Tree models wait.
