# Public datasets (SW-069)

Draft, updated 25 October 2026. Rows marked "to be checked" are confirmed when the file is downloaded. SitWise-Desk, our own recordings, is defined in `protocol.md` (SW-070).

The posture set for the public-data model is **MultiPosture**. The Roboflow sitting sets were reviewed and are not used.

## Why a public set is used

SitWise-Desk is the training and test set. A public set is used for three jobs:

1. The model trained only on public data is tested on SitWise-Desk (SW-085).
2. Fatigue needs hours of recording, and blinks need a label on each frame. We cannot collect that ourselves.
3. The blink method is measured on a set the literature already uses.

No public set matches a laptop camera from the front, with only the head, neck, and shoulders in frame. That is why SitWise-Desk is collected.

## Choice for each job

| Job | Selected set | Backup | Used for |
| --- | --- | --- | --- |
| Posture | MultiPosture (Zenodo) | None. Roboflow is not the backup | SW-085, the public-data model |
| Blinks | Eyeblink8 | Talking Face (FGNet), extra test only | EAR threshold against a model (SW-079) |
| Fatigue | UTA-RLDD, a subset | Rule-based score if access fails | SW-080, SW-083 |
| Distance | No public set | — | SitWise-Desk only, ruler labels (SW-019) |

## Posture

| Set | Size | Labels | Form | Licence | Camera angle | Fit |
| --- | --- | --- | --- | --- | --- | --- |
| MultiPosture (Zenodo, Carneros-Prado et al., 2024) | 4,800 frames, 13 people, 9.3 MB CSV | Torso: TUP upright, TLF forward, TLB backward, TLR/TLL right/left. Leg labels are also in the file | MediaPipe Pose 3D coordinates, 11 joints, normalized to the hip centre | CC BY 4.0 | Not stated, recorded at home | Selected. Already a MediaPipe CSV, so no video step. The set assumes the hip is visible. Our camera does not see the hip. To be checked |
| Roboflow, Sitting Posture Classification (khaldas-workspace) | 2,347 images | good_posture / bad_posture | Image classification | CC BY 4.0 | Not stated. To be checked | Not used. Two classes, and the angle may be mixed |
| Roboflow, Sitting_Posture (chrisworkspace) | 366 images | good_form / bad_form | Keypoints | CC BY 4.0 | Not stated. To be checked | Not used. Small |
| Roboflow, sitting-posture (thanya) | about 58–154 images | good / bad | Object detection | CC BY 4.0 | Not stated | Not used. Too small |
| Roboflow, sitting-posture-checker | 50 images | good / bad, plus broken labels ("baad", "gqe") | Object detection | CC BY 4.0 | Not stated | Not used. Too small, labels are broken |

**Decision.** SW-085 uses MultiPosture. The file is already landmark numbers, it has 13 people, the licence is CC BY 4.0, and the torso labels are closer to our commands than a good/bad image tag. Roboflow stays in the table as a set we looked at.

Mapping, once the joint list is confirmed: TUP → `dik`, TLF → `one_egik`, TLR and TLL → `yana_yatik`. TLB (leaning back) and the leg labels are not SitWise classes. `kambur` is not in this set, so the public-data model cannot learn a slouch from it.

Still to be checked: the names of the 11 joints. If the nose and both shoulders are present, the coordinates are re-normalized to the shoulder midpoint before training. If those joints are missing, MultiPosture cannot feed our feature columns, and SW-085 records that this public set does not fit the laptop camera.

## Blinks

| Set | Size | What is in it | Licence / access | Fit |
| --- | --- | --- | --- | --- |
| Eyeblink8 (Drutarovsky and Fogelton, ECCVW 2014) | 8 videos, 4 people, about 71,000 frames, 640×480 | Indoors, front view, fixed distance. Blinks are labelled frame by frame | Download page and licence to be checked | Selected. Front-facing webcam, close to a desk |
| Talking Face (FGNet) | 4 clips, 1 person, about 5,000 frames, 720×576 | One person talking | Open access on the FGNet page | Extra test only. One person |
| ZJU (Pan et al., ICCV 2007) | 80 clips, 20 people, about 10,900 frames, 320×240 | Short clips, front view | Access unclear | Not used. Low resolution |
| RT-BENE (Cortacero et al., ICCVW 2019) | Large, in the wild | Open or closed eye | Licence to be checked | Backlog, SW-094. Eye crops do not match our landmark pipeline |

**Decision.** Eyeblink8. It is the closest webcam setup, and the EAR method was tested on it (Soukupová and Čech, 2016), so the fixed-threshold comparison can be read against that paper.

Four people is a method check. The split is by person. The result is not a claim that the detector works for everyone.

## Fatigue

| Set | Size | What is in it | Licence / access | Fit |
| --- | --- | --- | --- | --- |
| UTA-RLDD (Ghoddoosian et al., CVPRW 2019) | 60 people (51 male, 9 female, ages 20–59), 180 videos, about 30 hours, **111.3 GB** | Three videos of about 10 minutes each: alert (0), low vigilance (5), drowsy (10). The label is the person's own report | Project page: sites.google.com/view/utarldd. Whether a form is required is to be checked. A licence is not stated. To be checked | Selected. People used their own phone or webcam indoors |

**Decision.** UTA-RLDD, as a subset.

The full 111.3 GB is not downloaded. A subset of about 15–20 people is downloaded first, and only the alert and drowsy videos. SW-080 turns those videos into minute-level feature rows. The video is not kept. The repository stores the feature CSV.

The roadmap target is a binary split, alert against drowsy, at or above 70%. The paper's 65.2% is a three-class result. The report does not compare those two numbers as if they were the same task.

The labels are self-reported. That limit is written on the model card.

If access has not arrived by 15 November, the fatigue score stays the rule (blink rate, PERCLOS, and posture deterioration) and is checked against the end-of-day 1–5 answers.

## Distance

No public set was found for screen distance. Distance labels exist only in SitWise-Desk, where the person sits at a ruler mark. The method is SW-019.

## Still open

- Eyeblink8 download page and licence.
- UTA-RLDD access. If a form is required, it has not been sent.
- The 11 joint names in MultiPosture.
- The advisor has not answered whether SitWise-Desk plus these public sets satisfies "find a dataset and train".

## Sources

- Ghoddoosian, R., Galib, M., and Athitsos, V. (2019). *A Realistic Dataset and Baseline Temporal Model for Early Drowsiness Detection.* CVPR Workshops. https://arxiv.org/abs/1904.07312
- Drutarovsky, T., and Fogelton, A. (2014). *Eye Blink Detection Using Variance of Motion Vectors.* ECCV Workshops.
- Soukupová, T., and Čech, J. (2016). *Real-Time Eye Blink Detection using Facial Landmarks.* CVWW.
- Hu, G., et al. (2019). *Towards Real-time Eyeblink Detection in The Wild: Dataset, Theory and Practices.* https://arxiv.org/abs/1902.07891
- Carneros-Prado, D., et al. (2024). *A Comparison Between Multilayer Perceptrons and Kolmogorov-Arnold Networks for Multi-Task Classification in Sitting Posture Recognition.* IEEE Access 12. Data: https://doi.org/10.5281/zenodo.14230872
- Roboflow Universe, Sitting Posture Classification: https://universe.roboflow.com/khaldas-workspace/sitting-posture-classification-ccvao-e9i4p
- Roboflow Universe, Sitting_Posture: https://universe.roboflow.com/chrisworkspace/sitting_posture
