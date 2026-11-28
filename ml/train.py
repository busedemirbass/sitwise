"""Compare posture and distance models on a leave-one-subject-out split.

SW-076. Logistic regression, a random forest and LightGBM see the same
training people as a threshold rule. Recordings stay outside the repository.

Run from the repository root:

    python -m ml.train posture --data /path/outside/the/repo
    python -m ml.train distance --data /path/outside/the/repo
"""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path

from sklearn.metrics import f1_score

from ml.data import (
    POSTURE_LABELS,
    distance_table,
    label_counts,
    latest_session_files,
    load_files,
    posture_table,
)
from ml.models import DISTANCE_MODELS, POSTURE_MODELS, predict_distance, predict_posture
from ml.rules import posture_rule_ready
from ml.split import loso

RESULTS = Path(__file__).resolve().parent / "results"
POSTURE_RESULTS = RESULTS / "posture.csv"
CONFUSION_RESULTS = RESULTS / "posture_confusion.csv"
DISTANCE_RESULTS = RESULTS / "distance.csv"
POSTURE_FIELDS = (
    "created_at",
    "task",
    "data_version",
    "people",
    "features",
    "model",
    "held_out",
    "n_train",
    "n_test",
    "macro_f1",
    "f1_dik",
    "f1_one_egik",
    "f1_kambur",
    "f1_yana_yatik",
    "note",
)
CONFUSION_FIELDS = (
    "created_at",
    "data_version",
    "model",
    "true_label",
    "predicted_label",
    "count",
)
DISTANCE_FIELDS = (
    "created_at",
    "task",
    "data_version",
    "people",
    "features",
    "model",
    "held_out",
    "n_train",
    "n_test",
    "mae",
    "mae_40",
    "mae_60",
    "mae_80",
    "note",
)
_COUNT_FIELDS = ("n_train", "n_test")
_RULERS = (40, 60, 80)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m ml.train")
    parser.add_argument("task", choices=("posture", "distance"))
    parser.add_argument(
        "--data",
        required=True,
        type=Path,
        help="Folder of pilot CSVs. This folder is outside the git repository.",
    )
    parser.add_argument("--results", type=Path)
    args = parser.parse_args(argv)
    try:
        files, skipped = latest_session_files(args.data)
        rows, version = load_files(files)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 2
    if args.task == "posture":
        return _posture(rows, version, skipped, args.results or POSTURE_RESULTS)
    return _distance(rows, version, skipped, args.results or DISTANCE_RESULTS)


def _posture(
    rows: list[dict[str, str]],
    version: str,
    skipped: list[str],
    destination: Path,
) -> int:
    try:
        table, features, notes = posture_table(rows)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 2
    models = list(POSTURE_MODELS)
    if not posture_rule_ready(features):
        models.remove("rule")
        notes.append(
            "rule skipped: it needs neckRatio, shoulderTilt and noseShoulderDrop"
        )
    notes = [*skipped, *notes, "each row is one frame, about 0.2 s apart"]
    _print_posture_plan(rows, table, features, notes)
    written = _run_posture(
        table, features, models, version, "; ".join(notes), destination
    )
    print(f"Wrote {written} result rows to {destination}")
    return 0


def _distance(
    rows: list[dict[str, str]],
    version: str,
    skipped: list[str],
    destination: Path,
) -> int:
    try:
        table, features, notes = distance_table(rows)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 2
    notes = [*skipped, *notes, "error is the absolute difference from the ruler, in cm"]
    _print_distance_plan(table, features, notes)
    written = _run_distance(table, features, version, "; ".join(notes), destination)
    print(f"Wrote {written} result rows to {destination}")
    return 0


def _run_posture(
    rows: list[dict[str, str]],
    features: list[str],
    models: list[str],
    version: str,
    note: str,
    destination: Path,
) -> int:
    people = ",".join(sorted({row["person_code"] for row in rows}))
    created = datetime.now().astimezone().isoformat(timespec="seconds")
    result_rows: list[dict[str, str]] = []
    confusion = {
        model: {true: {pred: 0 for pred in POSTURE_LABELS} for true in POSTURE_LABELS}
        for model in models
    }
    for held_out, train, test in loso(rows):
        y_test = [row["label"] for row in test]
        for model in models:
            predicted = predict_posture(train, test, features, model)
            for true, pred in zip(y_test, predicted, strict=True):
                confusion[model][true][pred] += 1
            scores = _f1(y_test, predicted)
            scores["n_train"] = len(train)
            scores["n_test"] = len(test)
            result_rows.append(
                _record(
                    POSTURE_FIELDS,
                    created,
                    "posture",
                    version,
                    people,
                    features,
                    model,
                    held_out,
                    scores,
                    note,
                )
            )
            _print_posture_fold(model, held_out, scores)
    result_rows.extend(
        _means(
            result_rows,
            POSTURE_FIELDS,
            created,
            "posture",
            version,
            people,
            features,
            note,
        )
    )
    _append(destination, POSTURE_FIELDS, result_rows)
    _append(
        destination.parent / "posture_confusion.csv",
        CONFUSION_FIELDS,
        _confusion_rows(confusion, created, version),
    )
    return len(result_rows)


def _run_distance(
    rows: list[dict[str, str]],
    features: list[str],
    version: str,
    note: str,
    destination: Path,
) -> int:
    people = ",".join(sorted({row["person_code"] for row in rows}))
    created = datetime.now().astimezone().isoformat(timespec="seconds")
    result_rows: list[dict[str, str]] = []
    for held_out, train, test in loso(rows):
        for model in DISTANCE_MODELS:
            predicted = predict_distance(train, test, model)
            scores = _distance_scores(test, predicted)
            scores["n_train"] = len(train)
            scores["n_test"] = len(test)
            result_rows.append(
                _record(
                    DISTANCE_FIELDS,
                    created,
                    "distance",
                    version,
                    people,
                    features,
                    model,
                    held_out,
                    scores,
                    note,
                )
            )
            print(
                f"{model} held out {held_out}: "
                f"train {scores['n_train']}, test {scores['n_test']}, "
                f"MAE {float(scores['mae']):.2f} cm"
            )
    result_rows.extend(
        _means(
            result_rows,
            DISTANCE_FIELDS,
            created,
            "distance",
            version,
            people,
            features,
            note,
        )
    )
    _append(destination, DISTANCE_FIELDS, result_rows)
    return len(result_rows)


def _f1(y_true: list[str], y_pred: list[str]) -> dict[str, float]:
    per_class = f1_score(
        y_true,
        y_pred,
        labels=list(POSTURE_LABELS),
        average=None,
        zero_division=0,
    )
    macro = f1_score(
        y_true,
        y_pred,
        labels=list(POSTURE_LABELS),
        average="macro",
        zero_division=0,
    )
    scores = {"macro_f1": float(macro)}
    for label, value in zip(POSTURE_LABELS, per_class, strict=True):
        scores[f"f1_{label}"] = float(value)
    return scores


def _distance_scores(
    test: list[dict[str, str]],
    predicted: list[float],
) -> dict[str, float]:
    truths = [float(row["distance_cm"]) for row in test]
    scores = {"mae": _mae(list(zip(truths, predicted, strict=True)))}
    for ruler in _RULERS:
        bucket = [
            (truth, guess)
            for truth, guess in zip(truths, predicted, strict=True)
            if truth == ruler
        ]
        scores[f"mae_{ruler}"] = _mae(bucket)
    return scores


def _mae(pairs: list[tuple[float, float]]) -> float:
    if not pairs:
        return 0.0
    return sum(abs(truth - guess) for truth, guess in pairs) / len(pairs)


def _means(
    fold_rows: list[dict[str, str]],
    fields: tuple[str, ...],
    created: str,
    task: str,
    version: str,
    people: str,
    features: list[str],
    note: str,
) -> list[dict[str, str]]:
    score_fields = [
        field
        for field in fields
        if field not in _record_fields() and field not in _COUNT_FIELDS
    ]
    means: list[dict[str, str]] = []
    for model in _model_order(fold_rows):
        group = [row for row in fold_rows if row["model"] == model]
        averaged: dict[str, float | int] = {
            key: sum(float(row[key]) for row in group) / len(group)
            for key in (*_COUNT_FIELDS, *score_fields)
        }
        means.append(
            _record(
                fields,
                created,
                task,
                version,
                people,
                features,
                model,
                "mean",
                averaged,
                note
                + "; mean of the held-out person folds; each person weighs the same",
            )
        )
        if task == "posture":
            print(f"{model} mean macro F1 {float(averaged['macro_f1']):.3f}")
        else:
            print(f"{model} mean MAE {float(averaged['mae']):.2f} cm")
    return means


def _record_fields() -> set[str]:
    return {
        "created_at",
        "task",
        "data_version",
        "people",
        "features",
        "model",
        "held_out",
        "note",
    }


def _model_order(rows: list[dict[str, str]]) -> list[str]:
    seen: list[str] = []
    for row in rows:
        if row["model"] not in seen:
            seen.append(row["model"])
    return seen


def _record(
    fields: tuple[str, ...],
    created: str,
    task: str,
    version: str,
    people: str,
    features: list[str],
    model: str,
    held_out: str,
    scores: dict[str, float | int],
    note: str,
) -> dict[str, str]:
    row = {
        "created_at": created,
        "task": task,
        "data_version": version,
        "people": people,
        "features": ",".join(features),
        "model": model,
        "held_out": held_out,
        "note": note,
    }
    for key, value in scores.items():
        if key in _COUNT_FIELDS:
            row[key] = str(int(round(float(value))))
        else:
            row[key] = f"{float(value):.4f}"
    for field in fields:
        row.setdefault(field, "")
    return row


def _confusion_rows(
    confusion: dict[str, dict[str, dict[str, int]]],
    created: str,
    version: str,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for model, matrix in confusion.items():
        for true in POSTURE_LABELS:
            for pred in POSTURE_LABELS:
                rows.append(
                    {
                        "created_at": created,
                        "data_version": version,
                        "model": model,
                        "true_label": true,
                        "predicted_label": pred,
                        "count": str(matrix[true][pred]),
                    }
                )
    return rows


def _append(
    destination: Path, fields: tuple[str, ...], rows: list[dict[str, str]]
) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    write_header = not destination.exists() or destination.stat().st_size == 0
    with destination.open("a", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), lineterminator="\n")
        if write_header:
            writer.writeheader()
        writer.writerows(rows)


def _print_posture_plan(
    raw: list[dict[str, str]],
    table: list[dict[str, str]],
    features: list[str],
    notes: list[str],
) -> None:
    print("Posture labels kept:", ", ".join(POSTURE_LABELS))
    print("Rows in the files:", dict(sorted(label_counts(raw).items())))
    print("Rows used for posture:", dict(sorted(label_counts(table).items())))
    print("Features used:", ", ".join(features))
    for note in notes:
        print("Note:", note)


def _print_distance_plan(
    table: list[dict[str, str]],
    features: list[str],
    notes: list[str],
) -> None:
    print("Rows used for distance:", len(table))
    print("Features used:", ", ".join(features))
    for note in notes:
        print("Note:", note)


def _print_posture_fold(
    model: str, held_out: str, scores: dict[str, float | int]
) -> None:
    per_class = " ".join(
        f"{label}={float(scores[f'f1_{label}']):.3f}" for label in POSTURE_LABELS
    )
    print(
        f"{model} held out {held_out}: "
        f"train {scores['n_train']}, test {scores['n_test']}, "
        f"macro F1 {float(scores['macro_f1']):.3f} ({per_class})"
    )


if __name__ == "__main__":
    raise SystemExit(main())
