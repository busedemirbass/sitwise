# SitWise — Related Applications and Literature Comparison (v2)

> **Card:** SW-024  
> **Track:** B (Report / Documentation / Server)  
> **Reference:** SitWise Roadmap v2: Model, Dataset, and Task Plan (21 October 2026)  
> **Target:** Midterm Report & References List for Report — Chapter 2 (Literature Review and Comparison of Existing Systems)  
> **Date:** October 2026  
> **Status:** Completed  

---

## 1. Introduction and Scope

Prolonged screen exposure and physical inactivity among desk workers trigger musculoskeletal disorders (particularly forward head posture / cervical straightening, shoulder asymmetry, kyphosis) and symptoms of Digital Eye Strain (Computer Vision Syndrome - CVS). Aligned with the United Nations Sustainable Development Goal 3 (Good Health and Well-Being), **SitWise** is a privacy-first desktop ergonomics assistant that monitors posture, screen distance, blink frequency, and fatigue using only a standard laptop or webcam.

With the **SitWise Roadmap v2**, the project's focus shifted from a simple prototype reliant solely on fixed rules and threshold checks to **trained machine learning models running locally on-device**, a **custom imageless coordinate-based dataset (SitWise-Desk)**, and **rigorous, comparative experimental validation (LOSO)**.

This document presents:
1. Limitations of existing commercial, open-source, and academic systems,
2. A multi-dimensional comparison matrix between SitWise and alternative solutions,
3. The rationale for why off-the-shelf data is insufficient and the SitWise-Desk dataset strategy,
4. Literature review on posture, blink, and fatigue detection,
5. Academic bibliography and references for reporting.

---

## 2. Existing Systems and Key Limitations

Solutions in the market and literature generally fall into four main categories:

### 2.1. Commercial Camera-Based Tools (e.g., BLiiNK)
* **Overview:** A commercial desktop tool that monitors blink frequency, screen distance, and basic sitting posture via a standard webcam.
* **Limitations:**
  * **Proprietary and Fixed Thresholds:** Decision mechanisms are closed-source; they do not adapt dynamically to diverse sitting habits and working environments.
  * **No False Positive Management:** Lacks a feedback loop that learns from false alarms triggered when the user yawns, drinks water, or shifts position, leading to alert fatigue.
  * **Image Processing Trust:** Being closed-source, it fails to fully alleviate enterprise privacy concerns regarding the handling of raw video streams.

### 2.2. Simple Posture Tracking Tools (e.g., Posturr)
* **Overview:** Open/semi-open source desktop utilities that check whether the user is sitting upright using a webcam.
* **Limitations:**
  * Only tracks torso tilt; fails to observe blink reflex (CVS), screen distance, or mental/physical fatigue.
  * Lacks session tracking, time-series analytics, and a historical reporting layer.
  * Dependent on simple pixel or landmark offset thresholds rather than trained models, collapsing under varying camera angles.

### 2.3. Timer and Break Utilities (e.g., SitApp, Pomodoro Tools)
* **Overview:** Rule-based applications prompting break reminders at regular intervals (such as the 20-20-20 rule or Pomodoro technique).
* **Limitations:**
  * No biomechanical or visual tracking; unaware of whether the user is actually slouching, leaning too close to the screen, or experiencing reduced blink rates.
  * Emits notifications on rigid time schedules without accounting for the user's actual fatigue state.

### 2.4. Wearable Sensors (e.g., Upright GO, Smart Posture Braces)
* **Overview:** Physical hardware devices containing accelerometers and gyroscopes (IMUs) affixed to the spine or worn around the neck.
* **Limitations:**
  * High supplementary hardware cost (initial purchase, replacement adhesive strips, etc.).
  * Must be worn physically, leading to low long-term user comfort and adoption rates.
  * Incapable of measuring eye strain or screen distance; requires continuous battery charging.

### 2.5. Typical Academic Models and Literature Prototypes
* **Overview:** Published papers and proof-of-concept scripts using computer vision frameworks such as MediaPipe, OpenPose, and Soukupová & Čech's EAR algorithm.
* **Limitations (Off-the-Shelf Data & Evaluation Pitfalls):**
  * **Domain Mismatch:** Academic posture datasets typically feature side-profile views, standing subjects, or synthetic robotic motions. They do not capture the realistic front-facing laptop webcam angle or natural desk activities like typing and phone usage.
  * **Data Leakage:** Many studies randomly split video frames from the same subjects across both training and test sets, falsely reporting 95%+ accuracy. Performance degrades dramatically when evaluated on unseen subjects.
  * **Lack of Productization:** Work predominantly remains confined to Jupyter notebooks; it is rarely converted into an end-to-end product with lightweight on-device ONNX inference, OS system tray integration, and a full client-server architecture.

---

## 3. Comparison Matrix

The table below provides a comprehensive comparison between SitWise (Roadmap v2) and alternative solutions across industry and academia:

| Comparison Metric | SitWise (Roadmap v2) | BLiiNK | Posturr | SitApp / Pomodoro | Upright GO | Typical Academic Study |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Required Hardware** | Standard Laptop Webcam | Standard Webcam | Standard Webcam | No Hardware | Dedicated IMU Device | Camera / High-End GPU |
| **Additional Hardware Cost** | **$0 / Free** | $0 | $0 | $0 | High Hardware Cost | Variable |
| **Posture Detection** | **Trained Model (4 Classes) + Normalization** | Rule-based / Closed | Simple Threshold | None | Tilt Sensor | Model (Often single class/angle) |
| **Blink Detection (CVS)** | **EAR + Time Window Analytics** | Yes | None | None | None | Yes (Only raw EAR formula) |
| **Screen Distance Measurement**| **Iris Diameter + Regression (40/60/80 cm)** | Yes | Limited | None | None | Limited / Depth Camera |
| **Early Fatigue Detection** | **Multi-Metric (PERCLOS, Blinks, Yawns, Head)** | Simple timer | None | None | None | Driver drowsiness models only |
| **Model Runtime Location** | **On-Device ONNX Runtime (CPU ≤ 15%, ≤10 ms)** | Client | Client | Client | Microcontroller | Python / Cloud / GPU |
| **Privacy Guarantee** | **Imageless (Processed in RAM; disk/network = 0 frames)** | Partially Local | Local | No Camera | Sensor Data Only | Often raw dataset video |
| **Custom Desk Dataset** | **Yes (SitWise-Desk: 7-step protocol)** | Unknown (Closed) | None | None | None | Synthetic / Side-view sets |
| **Rigorous Evaluation (LOSO)**| **Yes (Unseen subject evaluation, LOSO)** | None / Unspecified | None | None | None | Rarely (Mostly random split) |
| **Comparative Experiment** | **4 Approaches (Rule, Off-the-Shelf, Custom, Personalized)** | None | None | None | None | Usually single model |
| **Personalization** | **5s Calibration + Threshold Shift via "Wrong Alert"** | None | Limited | None | Button Reset | None / Fixed Threshold |
| **External CDN Dependency** | **None (Bundled local Wasm & models)** | Unspecified | Variable | None | Mobile App | Often CDN-dependent |
| **Client Architecture** | **Isolated Electron (Context Isolation, Sandbox)**| Closed source | Variable | Standard | Mobile UI | Notebook / Script |
| **Sessions and Scoring** | **PostgreSQL + 0–100 Daily Ergonomics Score** | Yes (Cloud) | None | Basic Counter | Yes (Mobile) | None |
| **Open Data / Scientific Artifacts** | **Model Card, Data Card, Anonymized Dataset** | None (Commercial) | Partial Code | Partial Code | None | Paper Only |

---

## 4. Key Innovations and Differentiators of SitWise v2

SitWise v2 is not a trivial wrapper around off-the-shelf libraries. The system is differentiated from existing academic and school projects by seven core engineering pillars:

### 4.1. Designing and Collecting Purpose-Fit Data, Not Just "Training a Model" (SitWise-Desk)
Most computer vision projects download a generic internet dataset and report 95% accuracy on that same data, failing to answer the critical jury question: *"Does this data actually fit your deployment environment?"*
* Pre-existing posture datasets (Roboflow, etc.) predominantly contain side-angle footage or standing individuals.
* SitWise engineered the **SitWise-Desk** dataset, tailored specifically to front-facing laptop webcam perspectives and realistic desk-sitting behaviors.
* Data is captured via a structured 7-step scenario protocol: baseline calibration, upright, forward lean, slouching, sideways lean, 40/60/80 cm distances, and unconstrained free work.
* Experiment **SW-085** provides quantitative evidence answering why off-the-shelf data fails in our setup.

### 4.2. Imageless Data and Lightweight On-Device Inference (ONNX)
* **Zero image frames are ever stored or transmitted** across both dataset recording and runtime execution.
* MediaPipe Tasks (FaceLandmarker and PoseLandmarker) extract instantaneous 3D coordinates from the camera feed in RAM, converting them immediately to scalar features (neck angle, shoulder tilt, nose-shoulder distance, iris diameter, EAR).
* Trained lightweight ML models (Logistic Regression, Random Forest, LightGBM) are **exported to ONNX format and executed on the client via ONNX Runtime** (inference time ≤ 10 ms per frame, CPU utilization ≤ 15%).
* The server (FastAPI + PostgreSQL) receives only periodic numeric session summaries and scalar metrics.

### 4.3. Methodological Rigor and Honest Evaluation (LOSO)
* The pervasive machine learning pitfall of data leakage (allocating frames of the same individual to both training and test sets) is strictly eliminated.
* Evaluations are conducted using **Leave-One-Subject-Out (LOSO)** cross-validation.
* Final model generalization is validated on an independent **volunteer test set** of 10–15 unseen subjects (targeting Macro F1 ≥ 0.85).

### 4.4. Comparative Experiment Across 4 Approaches
The midterm evaluation and final deliverables benchmark four distinct approaches side-by-side on the exact same unseen test set:
1. Rule-based fixed thresholds
2. Model trained solely on off-the-shelf data (Roboflow, etc.)
3. Model trained on our custom dataset (SitWise-Desk)
4. Personalized model (+ 5-second calibration and user-driven threshold adaptation)

### 4.5. Measurable Two-Stage Personalization
Static models produce high false-positive rates due to anatomical and environmental variance (desk height, user height, camera angle).
* **Stage 1 (Normalization):** A 5-second upright calibration at session start captures individual baseline metrics (`mean`, `std`), scaling subsequent features relative to this baseline.
* **Stage 2 (Learned Threshold Shift - SW-046):** When the user clicks the **"Wrong Alert"** button in the UI, the decision threshold for that specific user shifts dynamically without retraining the model. The measurable success criterion is a **≥ 30% reduction** in false alerts.

### 4.6. Multi-Dimensional Fatigue Estimation (UTA-RLDD & Behavioral Metrics)
Rather than acting as a simple break clock, SitWise fuses:
* Blink frequency,
* PERCLOS (Percentage of Eye Closure),
* Mean blink duration,
* Mouth Aspect Ratio (MAR - yawning detection),
* Head nods / drops,
* Posture deterioration frequency,
into a 0–100 fatigue score computed over rolling 1-minute windows. The underlying model is verified against the academic UTA-RLDD dataset and correlated with user end-of-day self-reports (1–5 scale).

### 4.7. Professional Documentation: Model Card and Dataset Card
Adhering to international standards in machine learning ethics and reproducibility:
* A **Dataset Card (Datasheet)** detailing collection protocols, consent procedures, and demographic distributions,
* A **Model Card** documenting performance breakdowns, limitations, and input/output contracts,
will be published anonymously on Zenodo/GitHub as an open-science contribution.

---

## 5. Literature Review and Theoretical Foundations

### 5.1. Blink Detection and Digital Eye Strain (CVS)
* **Underlying Problem:** Desk workers experiencing prolonged cognitive focus show a decrease in blink rate from a normal 15–20 blinks/min down to 5–7 blinks/min, causing dry eyes, ocular fatigue, and headaches (Blehm et al., 2005; Gowrisankaran & Sheedy, 2015).
* **Eye Aspect Ratio (EAR) Methodology:** Soukupová & Čech (2016) introduced the EAR metric, calculating the ratio of vertical eyelid distances to horizontal eye width via facial landmarks:
  $$\text{EAR} = \frac{||p_2 - p_6|| + ||p_3 - p_5||}{2 ||p_1 - p_4||}$$
* **SitWise Implementation:** EAR time series are computed across 6 facial landmarks per eye using MediaPipe FaceLandmarker. A fixed EAR threshold is benchmarked against window-based classifiers referencing Eyeblink8 and RT-BENE datasets, tracking blink count with minute-level precision (±2 blinks tolerance).

### 5.2. Posture Analysis and Biomechanics
* **Forward Head Posture and Kyphosis:** For every 2.5 cm the head moves forward from neutral alignment, cervical spine loading increases by approximately 4.5–5 kg. Cagnie et al. (2007) identified sustained static, forward-flexed posture as a leading risk factor for neck pain among office workers.
* **Landmark-Based Posture Estimation:** Deep learning models such as OpenPose (Cao et al., 2017) and MediaPipe Pose / BlazePose (Bazarevsky et al., 2020) enable real-time human joint tracking.
* **Why Off-the-Shelf Data Falls Short:** Existing public sets (e.g., Roboflow posture datasets) typically capture subjects from side views or third-person perspectives. SitWise operates under front-facing camera angles 40–80 cm from the user where only the head and upper torso are visible. SitWise computes head pitch, neck ratio, nose-shoulder vertical offset, and shoulder tilt as baseline-relative features.

### 5.3. Fatigue Detection and PERCLOS
* **PERCLOS Metric:** Developed by Wierwille et al. (1994), PERCLOS denotes the proportion of time the eyelids remain 80% or more closed (P80) over a designated interval. It remains the gold standard in computer vision for detecting drowsiness and lapses in vigilance.
* **UTA-RLDD Dataset:** Ghoddoosian & Zhu (2019) introduced the UTA Real-Life Drowsiness Dataset (UTA-RLDD), comprising 60 subjects and 30 hours of video labeled into alert, low-vigilant, and drowsy states. SitWise utilizes this benchmark to train and validate its fatigue scoring pipeline.

### 5.4. Machine Learning Evaluation Methodology and Transparency
* **Mitigating Data Leakage (LOSO):** When standard random k-fold cross-validation is applied to biometric video sequences, frames of the same subject leak into both train and test splits. Leave-One-Subject-Out (LOSO) cross-validation is mandatory to evaluate true cross-subject generalization.
* **Model and Data Cards:** Established by Mitchell et al. (2019) (*Model Cards*) and Gebru et al. (2021) (*Datasheets for Datasets*), these artifacts ensure transparency regarding algorithmic limitations, ethical considerations, and training dataset composition.

---

## 6. References for Report and Presentations

1. **Soukupová, T., & Čech, J. (2016).** *Real-Time Eye Blink Detection using Facial Landmarks.* 21st Computer Vision Winter Workshop (CVWW), Rimske Toplice, Slovenia.
2. **Ghoddoosian, R., & Zhu, M. (2019).** *A Realistic Dataset and Baseline Temporal Model for Detecting Depression/Drowsiness using Facial Landmarks.* Proceedings of the IEEE/CVF International Conference on Computer Vision (ICCV) Workshops, pp. 0-0. [UTA-RLDD Dataset].
3. **Lugaresi, C., Tang, J., Nash, H., McClanahan, C., Uboweja, E., Hays, M., ... & Grundmann, M. (2019).** *MediaPipe: A Framework for Building Perception Pipelines.* arXiv preprint arXiv:1906.08172.
4. **Bazarevsky, V., Grishchenko, I., Raveendran, K., Zhu, T., Zhang, F., & Grundmann, M. (2020).** *BlazePose: On-device Real-time Body Pose Tracking.* arXiv preprint arXiv:2006.10204.
5. **Blehm, C., Vishnu, S., Khattak, A., Mitra, S., & Yee, R. W. (2005).** *Computer Vision Syndrome: A Review.* Survey of Ophthalmology, 50(3), 253-262.
6. **Gowrisankaran, S., & Sheedy, J. E. (2015).** *Computer vision syndrome: A review.* Work: A Journal of Prevention, Assessment and Rehabilitation, 52(2), 303-314.
7. **Cagnie, B., Danneels, L., Van Tiggelen, D., De Loose, V., & Cambier, D. (2007).** *Individual and work related risk factors for neck pain among office workers: A cross sectional study.* European Spine Journal, 16(5), 679-686.
8. **Wierwille, W. W., Ellsworth, L. A., Wreggit, S. S., Fairbanks, R. J., & Kirn, C. L. (1994).** *Research on Vehicle-Based Driver Status/Performance Monitoring; Development, Validation, and Refinement of Algorithms for Detection of Driver Drowsiness.* National Highway Traffic Safety Administration (NHTSA) Technical Report, DOT-HS-808-247.
9. **Fuhl, W., Santini, T., Kasneci, G., & Kasneci, E. (2018).** *RT-BENE: A Dataset and Benchmark for Real-Time Blink Estimation in Natural Environments.* ACM Symposium on Eye Tracking Research and Applications (ETRA).
10. **Ke, G., Meng, Q., Finley, T., Wang, T., Chen, W., Ma, W., ... & Liu, T. Y. (2017).** *LightGBM: A Highly Efficient Gradient Boosting Decision Tree.* Advances in Neural Information Processing Systems (NeurIPS), 30.
11. **Mitchell, M., Wu, S., Zaldivar, A., Barnes, P., Vasserman, L., Hutchinson, B., ... & Gebru, T. (2019).** *Model Cards for Model Reporting.* Proceedings of the Conference on Fairness, Accountability, and Transparency (FAT*), pp. 220-229.
12. **Gebru, T., Morgenstern, J., Vecchione, B., Vaughan, J. W., Wallach, H., Daumé III, H., & Crawford, K. (2021).** *Datasheets for Datasets.* Communications of the ACM, 64(12), 86-92.
13. **Electron Security Guidelines. (2024).** *Context Isolation and Sandboxing in Desktop Applications.* ElectronJS Documentation. https://www.electronjs.org/docs/latest/tutorial/security
