# Data collection protocol (SW-070)

This is the script for one SitWise-Desk recording. It is a draft. The consent form is [`consent-form.md`](consent-form.md). The advisor has not seen either file. Whether this form is enough, or an ethics board is required, is still an open question in the kickoff note. This file does not record an approval.

The first recordings are the two teammates. People outside the team are not recorded until the advisor has seen the form and answered that question.

## What a session is

One person, one sitting, about 10 minutes. The commands themselves take 7 minutes 35 seconds. The app shows one command at a time. While a command is on screen, the app writes about five rows a second. The label on those rows is the command. The camera frame is not written.

A second sitting in the other light is useful when the person agrees. It is a new session id, the same person code.

## Before the session

1. The person reads and signs `consent-form.md`. The signed paper stays with the team. It is not committed to the repository, and it is not a camera image.
2. The operator assigns a person code such as `P07`. The code is not a name.
3. The operator records three facts for the whole session: glasses `var` or `yok`, light `iyi` or `zayif`, camera `laptop` or `harici`.
4. The person sits at the desk. A ruler is on the desk for step 6.

## Commands

| Step | What the person does | Duration | `label` | `distance_cm` |
| --- | --- | --- | --- | --- |
| 1 | Sit upright and look at the screen | 5 s | `kalibrasyon` | empty |
| 2 | Sit upright, type and read | 60 s | `dik` | empty |
| 3 | Lean the head forward | 45 s | `one_egik` | empty |
| 4 | Slouch and drop the shoulders | 45 s | `kambur` | empty |
| 5 | Lean right, then left | 30 s, then 30 s | `yana_yatik` | empty |
| 6 | Sit at 40 cm, then 60 cm, then 80 cm, checked with the ruler | 20 s each | `mesafe_cm` | `40`, then `60`, then `80` |
| 7 | Work freely, with no posture command | 3 min | `serbest` | empty |

Step 7 is the sitting used later for the false-alert count. The person is not told to hold a pose.

## What each row contains

One CSV per session. Example name: `P07_S01_2026-10-23.csv`. The file stays in the recordings folder on the computer. Raw rows are not committed.

| Column | What it stores |
| --- | --- |
| `person_code` | Anonymous code, the same on every row of the session |
| `session` | Session id, such as `S01` |
| `t_s` | Seconds from the start of the session |
| feature columns | The names in [`features.md`](features.md). A feature the app cannot compute yet is left empty. This protocol does not add a formula |
| `label` | The command token from the table above |
| `distance_cm` | The ruler value. Filled only on step 6. Empty on the other steps |
| `camera` | `laptop` or `harici` |
| `glasses` | `var` or `yok` |
| `light` | `iyi` or `zayif` |

`camera`, `glasses`, and `light` are chosen once and repeated on every row, so a row can be read on its own.

The screen may show the command in English. The file stores the tokens in the table, not the English sentence.

## After the session

The operator checks that the file has rows, that step 6 contains 40, 60, and 80, and that the file contains no image. If the person stops or withdraws, that session file is deleted and is not used.
