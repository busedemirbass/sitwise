"""
SW-073 Test Paketi: Hazır Veri Hattı (Track C).
Kabul Kriteri: Eyeblink8 ve seçilen duruş seti CSV'ye çevrildi.
"""

from __future__ import annotations

import csv
from pathlib import Path
import tempfile
import unittest

from scripts.pipeline.common import (
    LEFT_EYE_INDICES,
    RIGHT_EYE_INDICES,
    Point2D,
    compute_ear,
    compute_posture_features,
    euclidean_distance,
)
from scripts.pipeline.eyeblink8_pipeline import (
    CSV_HEADER as EB_HEADER,
    generate_eyeblink8_benchmark_csv,
)
from scripts.pipeline.posture_pipeline import (
    CSV_HEADER as MP_HEADER,
    generate_posture_benchmark_csv,
)


class TestDataPipelineSW073(unittest.TestCase):
    """SW-073 Veri Hattı birim testleri."""

    def test_euclidean_distance(self):
        p1 = Point2D(0.0, 0.0)
        p2 = Point2D(3.0, 4.0)
        self.assertAlmostEqual(euclidean_distance(p1, p2), 5.0)

    def test_compute_ear_open_and_closed(self):
        # 1. Açık göz simülasyonu (Sol ve Sağ göz indeksleri)
        open_left = {
            33: Point2D(0.0, 0.0),
            133: Point2D(10.0, 0.0),  # width = 10.0
            160: Point2D(3.0, -3.0),
            158: Point2D(7.0, -3.0),
            153: Point2D(7.0, 3.0),
            144: Point2D(3.0, 3.0),
        }
        ear_open_left = compute_ear(open_left, LEFT_EYE_INDICES)
        self.assertGreater(ear_open_left, 0.25)

        open_right = {
            362: Point2D(0.0, 0.0),
            263: Point2D(10.0, 0.0),
            385: Point2D(3.0, -3.0),
            387: Point2D(7.0, -3.0),
            373: Point2D(7.0, 3.0),
            380: Point2D(3.0, 3.0),
        }
        ear_open_right = compute_ear(open_right, RIGHT_EYE_INDICES)
        self.assertGreater(ear_open_right, 0.25)

        # 2. Kapalı göz simülasyonu
        closed_landmarks = {
            33: Point2D(0.0, 0.0),
            133: Point2D(10.0, 0.0),
            160: Point2D(3.0, -0.5),
            158: Point2D(7.0, -0.5),
            153: Point2D(7.0, 0.5),
            144: Point2D(3.0, 0.5),
        }
        ear_closed = compute_ear(closed_landmarks, LEFT_EYE_INDICES)
        self.assertLess(ear_closed, 0.15)

    def test_compute_ear_edge_cases(self):
        # Sıfır genişlik
        zero_landmarks = {idx: Point2D(0.0, 0.0) for idx in LEFT_EYE_INDICES}
        self.assertEqual(compute_ear(zero_landmarks, LEFT_EYE_INDICES), 0.0)

        # Hatalı indeks sayısı
        with self.assertRaises(ValueError):
            compute_ear(zero_landmarks, [33, 133])

    def test_compute_posture_features(self):
        # Dik duruş
        nose = Point2D(0.5, 0.3)
        left_s = Point2D(0.35, 0.6)
        right_s = Point2D(0.65, 0.6)
        left_ear = Point2D(0.38, 0.35)
        right_ear = Point2D(0.62, 0.35)

        feats = compute_posture_features(
            nose, left_s, right_s, left_ear, right_ear
        )
        self.assertAlmostEqual(feats["neckRatio"], 0.0, places=2)
        self.assertAlmostEqual(feats["shoulderTilt"], 0.0, places=2)
        self.assertGreater(feats["noseShoulderDrop"], 0.5)
        self.assertIsNotNone(feats["earShoulderDrop"])

        # Sıfır omuz genişliği
        zero_feats = compute_posture_features(nose, nose, nose)
        self.assertIsNone(zero_feats["neckRatio"])

    def test_eyeblink8_pipeline_csv_generation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_csv = Path(tmpdir) / "eyeblink_test.csv"
            rows = generate_eyeblink8_benchmark_csv(
                out_csv, num_people=2, frames_per_person=50
            )
            self.assertEqual(rows, 100)
            self.assertTrue(out_csv.exists())

            with open(out_csv, mode="r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader)
                self.assertEqual(header, EB_HEADER)
                row1 = next(reader)
                self.assertEqual(row1[0], "EB8_P01")
                self.assertIn(int(row1[7]), (0, 1))

    def test_posture_pipeline_csv_generation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_csv = Path(tmpdir) / "posture_test.csv"
            rows = generate_posture_benchmark_csv(
                out_csv, num_people=2, samples_per_label=5
            )
            # 2 kişi * 5 etiket * 5 örnek = 50 satır
            self.assertEqual(rows, 50)
            self.assertTrue(out_csv.exists())

            with open(out_csv, mode="r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader)
                self.assertEqual(header, MP_HEADER)
                row1 = next(reader)
                self.assertEqual(row1[0], "MP_P01")
                valid_labels = ("dik", "one_egik", "yana_yatik", "arkaya_yaslanmis")
                self.assertIn(row1[6], valid_labels)
