"""Checks for the loader and the person split. No pilot CSV is required."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ml.data import load_directory, posture_table
from ml.split import loso

HEADER = (
    "person_code,session,t_s,neckRatio,shoulderTilt,distanceCm,noseShoulderDrop,"
    "earShoulderDrop,headPitch,EAR,blinksPerMinute,PERCLOS,MAR,headDrop,label,"
    "distance_cm,camera,glasses,light"
)


def _row(person: str, label: str, neck: str, shoulder: str, drop: str) -> str:
    return (
        f"{person},S01,0.2,{neck},{shoulder},40,{drop},,,,,,,,{label},,laptop,yok,iyi"
    )


class SplitTest(unittest.TestCase):
    def test_loso_keeps_a_person_on_one_side(self) -> None:
        rows = [
            {"person_code": "P01", "label": "dik"},
            {"person_code": "P01", "label": "kambur"},
            {"person_code": "P02", "label": "dik"},
        ]
        folds = loso(rows)
        self.assertEqual([fold[0] for fold in folds], ["P01", "P02"])
        for held_out, train, test in folds:
            self.assertTrue(all(row["person_code"] != held_out for row in train))
            self.assertTrue(all(row["person_code"] == held_out for row in test))

    def test_one_person_is_refused(self) -> None:
        rows = [
            {"person_code": "P01", "label": "dik", "neckRatio": "0.1",
             "shoulderTilt": "0.0", "noseShoulderDrop": "0.7"},
        ]
        with self.assertRaises(ValueError):
            posture_table(rows)

    def test_empty_feature_and_other_labels_are_left_out(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            folder.joinpath("P01_S01_2026-10-27.csv").write_text(
                HEADER + "\n" + _row("P01", "dik", "0.1", "0.0", "") + "\n"
                + _row("P01", "serbest", "0.1", "0.0", "") + "\n",
                encoding="utf-8",
            )
            folder.joinpath("P02_S01_2026-11-21.csv").write_text(
                HEADER + "\n" + _row("P02", "dik", "0.2", "0.0", "0.4") + "\n"
                + _row("P02", "mesafe_cm", "0.2", "0.0", "0.4") + "\n",
                encoding="utf-8",
            )
            rows, _version = load_directory(folder)
            table, features, notes = posture_table(rows)
        self.assertEqual(features, ["neckRatio", "shoulderTilt"])
        self.assertTrue(any("noseShoulderDrop skipped" in note for note in notes))
        self.assertEqual({row["label"] for row in table}, {"dik"})
        self.assertEqual(len(table), 2)

    def test_image_cell_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            folder.joinpath("P01_S01_2026-10-27.csv").write_text(
                HEADER + "\n" + _row("P01", "dik", "data:image/png;base64,aaaa", "0", "0.7") + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                load_directory(folder)


if __name__ == "__main__":
    unittest.main()
