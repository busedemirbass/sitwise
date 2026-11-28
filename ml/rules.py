"""Posture thresholds taken from the training people only.

A slouch or a forward lean shortens the vertical gap from the shoulders to the
nose. A lean to either side moves the nose off the shoulder midpoint and tilts
the shoulders. The cut points are the midpoints between those class medians.
They are fit again on every training fold, so the held-out person does not
choose them.
"""

from __future__ import annotations

RULE_FEATURES = ("neckRatio", "shoulderTilt", "noseShoulderDrop")
_DROP_LABELS = ("dik", "one_egik", "kambur")


def posture_rule_ready(features: list[str]) -> bool:
    return all(name in features for name in RULE_FEATURES)


def predict_posture_rule(
    train: list[dict[str, str]],
    test: list[dict[str, str]],
) -> list[str]:
    side = [row for row in train if row["label"] == "yana_yatik"]
    other = [row for row in train if row["label"] != "yana_yatik"]
    if not side or not other:
        raise ValueError("The posture rule needs a side lean and another class.")
    neck_cut = (
        _median(_values(side, "neckRatio")) + _median(_values(other, "neckRatio"))
    ) / 2
    tilt_cut = (
        _median(_values(side, "shoulderTilt", absolute=True))
        + _median(_values(other, "shoulderTilt", absolute=True))
    ) / 2
    bands: list[tuple[float, str]] = []
    for label in _DROP_LABELS:
        group = [row for row in train if row["label"] == label]
        if not group:
            raise ValueError(f"The posture rule needs {label} rows in training.")
        bands.append((_median(_values(group, "noseShoulderDrop")), label))
    bands.sort(key=lambda item: item[0])
    low_cut = (bands[0][0] + bands[1][0]) / 2
    high_cut = (bands[1][0] + bands[2][0]) / 2
    predicted: list[str] = []
    for row in test:
        neck = float(row["neckRatio"])
        tilt = abs(float(row["shoulderTilt"]))
        if neck >= neck_cut or tilt >= tilt_cut:
            predicted.append("yana_yatik")
            continue
        drop = float(row["noseShoulderDrop"])
        if drop <= low_cut:
            predicted.append(bands[0][1])
        elif drop >= high_cut:
            predicted.append(bands[2][1])
        else:
            predicted.append(bands[1][1])
    return predicted


def _values(
    rows: list[dict[str, str]],
    feature: str,
    absolute: bool = False,
) -> list[float]:
    values = [float(row[feature]) for row in rows]
    if absolute:
        return [abs(value) for value in values]
    return values


def _median(values: list[float]) -> float:
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2
