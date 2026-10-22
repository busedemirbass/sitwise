# Vision and scope (SW-003)

SitWise is a privacy-first desktop assistant. It watches the posture, screen distance, blinks and fatigue of someone working at a desk, using only a normal webcam. The project is Graduation Project I at Manisa Celal Bayar University, Computer Engineering. Two people build it. The advisor is Arş. Gör. Dr. Ahmet Cahit Yaşa. It lines up with Sustainable Development Goal 3.

This file is the v2 scope. Roadmap v2, dated 21 October 2026, replaces the earlier plan of fixed thresholds only.

## What the user gets

The app sits in the tray and keeps watching while the person works. It learns a personal baseline from a few seconds of upright sitting. It warns gently when a bad posture stays. The person can mark a warning as wrong, and that answer moves their own threshold. A daily score and a simple timeline show the day. The computer they already have is enough. No extra camera, no wearable.

## What changed in v2

v1 scored posture with a fixed threshold plus calibration. v2 trains models on numbers, then still uses calibration to normalize those numbers and the false-alert button to personalize the threshold.

The numbers come from MediaPipe landmarks, not from pixels. Three public datasets and one dataset the team collects, SitWise-Desk, feed the same feature columns. SitWise-Desk is a laptop camera, a front view, and real desk tasks. Labels come from the command the app is showing. Distance is measured with a ruler. The published set contains no image.

The trained model runs on the user's computer with ONNX Runtime. The server receives only numeric summaries.

The midterm is a PDF form, not a long report. The time that frees goes to data and the first models. The final report does not claim one accuracy number. It compares four approaches on people the model never trained on: rule thresholds, a public-data model, the SitWise-Desk model, and the personalized threshold.

## In scope

- Electron desktop client, MediaPipe face and pose landmarks, on-device models.
- FastAPI and PostgreSQL for accounts, sessions, summaries and feedback.
- A recording mode that writes feature rows and labels to CSV and does not write frames.
- Training and evaluation scripts under `ml/`, rerunnable with one command.
- A volunteer test that is also the unseen-person test set.
- An installer, a short demo, a model card and a dataset card.

## Out of scope

- Saving or uploading an image or a video.
- Training a convolutional network on images.
- A mobile app.
- Medical diagnosis.

## How we will judge it

The targets live in `docs/requirements.md` once the SW-011 update is merged. The headline ones are: posture macro F1 at least 0.85 on unseen people, distance error at most 5 cm between 40 and 80 cm, and zero images on the network. A missed target is reported with the reason. That is still a valid result.

## Deliveries

| Delivery | When | What |
| --- | --- | --- |
| Topic | 2 October 2026, done | SitWise |
| Instructor approval | 9 October 2026, done | Approval form |
| Midterm form | 20 November 2026 | Progress, data plan, first model results |
| Final | Draft 27 December, delivery 31 December 2026 | Report, v1.0 installer, demo, dataset and model cards |
