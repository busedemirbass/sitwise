"""SW-076 checks. No pilot CSV is required."""

from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from ml.data import distance_table, latest_session_files, load_files
from ml.rules import predict_posture_rule
from ml.train import main

HEADER = (
    "person_code,session,t_s,neckRatio,shoulderTilt,distanceCm,noseShoulderDrop,"
    "earShoulderDrop,headPitch,EAR,blinksPerMinute,PERCLOS,MAR,headDrop,label,"
    "distance_cm,camera,glasses,light"
)


def _posture_row(person: str, label: str, neck: str, tilt: str, drop: str) -> str:
    return f"{person},S01,0.2,{neck},{tilt},50,{drop},,,,,,,,{label},,laptop,yok,iyi"


def _distance_row(person: str, iris: str, ruler: str) -> str:
    return (
        f"{person},S01,0.2,0.02,0.01,{iris},0.7,,,,,,,,mesafe_cm,{ruler},laptop,yok,iyi"
    )


class TrainTest(unittest.TestCase):
    def test_later_session_replaces_the_earlier_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            folder.joinpath("P01_S01_2026-10-27.csv").write_text(
                HEADER + "\n" + _posture_row("P01", "dik", "0.1", "0", "0.7") + "\n",
                encoding="utf-8",
            )
            folder.joinpath("P01_S01_2026-11-23.csv").write_text(
                HEADER + "\n" + _posture_row("P01", "kambur", "0.2", "0", "0.4") + "\n",
                encoding="utf-8",
            )
            folder.joinpath("P02_S01_2026-11-21.csv").write_text(
                HEADER + "\n" + _posture_row("P02", "dik", "0.1", "0", "0.7") + "\n",
                encoding="utf-8",
            )
            chosen, notes = latest_session_files(folder)
            rows, _version = load_files(chosen)
        self.assertEqual(
            [path.name for path in chosen],
            [
                "P01_S01_2026-11-23.csv",
                "P02_S01_2026-11-21.csv",
            ],
        )
        self.assertIn("skipped P01_S01_2026-10-27.csv", notes[0])
        self.assertEqual(
            {row["label"] for row in rows if row["person_code"] == "P01"}, {"kambur"}
        )

    def test_result_log_drops_a_nickname_in_the_file_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            folder.joinpath("P03_S01_2026-11-26(NICK).csv").write_text(
                HEADER + "\n" + _posture_row("P03", "dik", "0.1", "0", "0.7") + "\n",
                encoding="utf-8",
            )
            chosen, _notes = latest_session_files(folder)
            _rows, version = load_files(chosen)
        self.assertNotIn("NICK", version)
        self.assertIn("P03_S01_2026-11-26.csv", version)

    def test_rule_uses_side_lean_then_the_vertical_gap(self) -> None:
        train = [
            *_copies("P01", "dik", "0.02", "0.01", "0.80"),
            *_copies("P01", "one_egik", "0.02", "0.01", "0.30"),
            *_copies("P01", "kambur", "0.02", "0.01", "0.55"),
            *_copies("P01", "yana_yatik", "0.30", "0.20", "0.60"),
        ]
        test = [
            {"neckRatio": "0.30", "shoulderTilt": "0.01", "noseShoulderDrop": "0.60"},
            {"neckRatio": "0.02", "shoulderTilt": "0.01", "noseShoulderDrop": "0.30"},
            {"neckRatio": "0.02", "shoulderTilt": "0.01", "noseShoulderDrop": "0.55"},
            {"neckRatio": "0.02", "shoulderTilt": "0.01", "noseShoulderDrop": "0.80"},
        ]
        self.assertEqual(
            predict_posture_rule(train, test),
            ["yana_yatik", "one_egik", "kambur", "dik"],
        )

    def test_distance_table_keeps_the_ruler_step(self) -> None:
        rows = [
            {
                "person_code": "P01",
                "label": "dik",
                "distanceCm": "40",
                "distance_cm": "",
            },
            {
                "person_code": "P01",
                "label": "mesafe_cm",
                "distanceCm": "42",
                "distance_cm": "40",
            },
            {
                "person_code": "P01",
                "label": "mesafe_cm",
                "distanceCm": "10",
                "distance_cm": "15",
            },
            {
                "person_code": "P02",
                "label": "mesafe_cm",
                "distanceCm": "",
                "distance_cm": "60",
            },
            {
                "person_code": "P02",
                "label": "mesafe_cm",
                "distanceCm": "81",
                "distance_cm": "80",
            },
        ]
        kept, features, notes = distance_table(rows)
        self.assertEqual(features, ["distanceCm"])
        self.assertEqual(len(kept), 2)
        self.assertTrue(any("not 40, 60 or 80" in note for note in notes))
        self.assertTrue(any("empty" in note for note in notes))

    def test_command_writes_scores_and_a_confusion_matrix(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            _write_person(folder, "P01")
            _write_person(folder, "P02")
            results = folder / "posture.csv"
            code = main(["posture", "--data", str(folder), "--results", str(results)])
            self.assertEqual(code, 0)
            with results.open(newline="") as handle:
                score_rows = list(csv.DictReader(handle))
            with (folder / "posture_confusion.csv").open(newline="") as handle:
                matrix = list(csv.DictReader(handle))
        models = {row["model"] for row in score_rows}
        self.assertEqual(
            models,
            {"majority", "rule", "logistic_regression", "random_forest", "lightgbm"},
        )
        self.assertTrue(any(row["held_out"] == "mean" for row in score_rows))
        logistic = next(
            row
            for row in score_rows
            if row["model"] == "logistic_regression" and row["held_out"] == "mean"
        )
        self.assertGreater(float(logistic["macro_f1"]), 0.9)
        self.assertEqual(len(matrix), 5 * 4 * 4)
        self.assertTrue(
            all(row["true_label"] and row["predicted_label"] for row in matrix)
        )

    def test_distance_rule_reports_the_iris_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            for person, iris in (("P01", "50"), ("P02", "70")):
                lines = [HEADER]
                for ruler in ("40", "60", "80"):
                    lines.append(_distance_row(person, iris, ruler))
                folder.joinpath(f"{person}_S01_2026-11-23.csv").write_text(
                    "\n".join(lines) + "\n",
                    encoding="utf-8",
                )
            results = folder / "distance.csv"
            code = main(["distance", "--data", str(folder), "--results", str(results)])
            self.assertEqual(code, 0)
            with results.open(newline="") as handle:
                rows = list(csv.DictReader(handle))
        held = next(
            row for row in rows if row["model"] == "rule" and row["held_out"] == "P02"
        )
        # P02's iris is 70 against 40, 60 and 80: (30 + 10 + 10) / 3.
        self.assertEqual(held["mae"], "16.6667")


def _copies(
    person: str, label: str, neck: str, tilt: str, drop: str
) -> list[dict[str, str]]:
    return [
        {
            "person_code": person,
            "label": label,
            "neckRatio": neck,
            "shoulderTilt": tilt,
            "noseShoulderDrop": drop,
        }
        for _index in range(4)
    ]


def _write_person(folder: Path, person: str) -> None:
    pattern = {
        "dik": ("0.02", "0.00", "0.80"),
        "one_egik": ("0.02", "0.00", "0.30"),
        "kambur": ("0.02", "0.00", "0.55"),
        "yana_yatik": ("0.30", "0.25", "0.60"),
    }
    lines = [HEADER]
    for label, (neck, tilt, drop) in pattern.items():
        for _index in range(30):
            lines.append(_posture_row(person, label, neck, tilt, drop))
    folder.joinpath(f"{person}_S01_2026-11-23.csv").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    unittest.main()
