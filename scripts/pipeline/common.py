"""
SW-073: Hazır Veri Hattı Ortak Hesaplama ve Yardımcı Fonksiyonlar.
Track: C (Veri & Makine Öğrenimi / ML Pipeline)
Referanslar: docs/ml/features.md (SW-071), docs/ml/datasets.md (SW-069)
"""

from __future__ import annotations

import math
from typing import NamedTuple


class Point2D(NamedTuple):
    x: float
    y: float


def euclidean_distance(p1: Point2D, p2: Point2D) -> float:
    """İki nokta arasındaki Öklid mesafesini hesaplar."""
    return math.hypot(p1.x - p2.x, p1.y - p2.y)


def compute_ear(landmarks: dict[int, Point2D], eye_indices: list[int]) -> float:
    """Soukupová & Čech (2016) formülüne göre Eye Aspect Ratio (EAR) hesaplar.

    Formül: (|p2 - p6| + |p3 - p5|) / (2 * |p1 - p4|)
    eye_indices: [p1, p2, p3, p4, p5, p6]
    """
    if len(eye_indices) != 6:
        raise ValueError("Göz için tam 6 adet landmark indeksi gereklidir.")

    p1 = landmarks[eye_indices[0]]
    p2 = landmarks[eye_indices[1]]
    p3 = landmarks[eye_indices[2]]
    p4 = landmarks[eye_indices[3]]
    p5 = landmarks[eye_indices[4]]
    p6 = landmarks[eye_indices[5]]

    vertical1 = euclidean_distance(p2, p6)
    vertical2 = euclidean_distance(p3, p5)
    horizontal = euclidean_distance(p1, p4)

    if horizontal < 1e-6:
        return 0.0

    ear = (vertical1 + vertical2) / (2.0 * horizontal)
    return round(ear, 4)


# MediaPipe FaceMesh göz landmark indeksleri (docs/ml/features.md)
LEFT_EYE_INDICES = [33, 160, 158, 133, 153, 144]
RIGHT_EYE_INDICES = [362, 385, 387, 263, 373, 380]


def compute_posture_features(
    nose: Point2D,
    left_shoulder: Point2D,
    right_shoulder: Point2D,
    left_ear: Point2D | None = None,
    right_ear: Point2D | None = None,
) -> dict[str, float | None]:
    """docs/ml/features.md spesifikasyonuna göre duruş oranlarını hesaplar.

    Öznitelikler:
      - neckRatio: abs(nose.x - midX) / shoulderWidth
      - shoulderTilt: (left.y - right.y) / shoulderWidth
      - noseShoulderDrop: (midY - nose.y) / shoulderWidth
      - earShoulderDrop: Kulak-omuz mesafelerinin ortalaması / shoulderWidth
    """
    shoulder_width = euclidean_distance(left_shoulder, right_shoulder)
    if shoulder_width < 1e-5:
        return {
            "neckRatio": None,
            "shoulderTilt": None,
            "noseShoulderDrop": None,
            "earShoulderDrop": None,
        }

    mid_x = (left_shoulder.x + right_shoulder.x) / 2.0
    mid_y = (left_shoulder.y + right_shoulder.y) / 2.0

    neck_ratio = abs(nose.x - mid_x) / shoulder_width
    shoulder_tilt = (left_shoulder.y - right_shoulder.y) / shoulder_width
    nose_shoulder_drop = (mid_y - nose.y) / shoulder_width

    ear_shoulder_drop = None
    if left_ear is not None and right_ear is not None:
        drop_left = (left_shoulder.y - left_ear.y) / shoulder_width
        drop_right = (right_shoulder.y - right_ear.y) / shoulder_width
        ear_shoulder_drop = round((drop_left + drop_right) / 2.0, 4)

    return {
        "neckRatio": round(neck_ratio, 4),
        "shoulderTilt": round(shoulder_tilt, 4),
        "noseShoulderDrop": round(nose_shoulder_drop, 4),
        "earShoulderDrop": ear_shoulder_drop,
    }
