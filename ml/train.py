"""Fit one posture classifier on a leave-one-subject-out split and log the row.

This is the SW-084 skeleton. It does not choose among logistic regression,
random forest and LightGBM. That comparison is SW-076. With two people the
score only shows that the pipe runs.

Run from the repository root:

    python -m ml.train posture --data /path/outside/the/repo
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.preprocessing import StandardScaler

from ml.data import POSTURE_LABELS, label_counts, load_directory, posture_table
from ml.split import loso

RESULTS = Path(__file__).resolve().parent / "results" / "posture.csv"
FIELDS = (
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m ml.train")
    parser.add_argument("task", choices=("posture",))
    parser.add_argument(
        "--data",
        required=True,
        type=Path,
        help="Folder of pilot CSVs. This folder is outside the git repository.",
    )
    parser.add_argument("--results", type=Path, default=RESULTS)
    args = parser.parse_args(argv)
    try:
        rows, version = load_directory(args.data)
        table, features, notes = posture_table(rows)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 2
    _print_plan(rows, table, features, notes)
    written = _run(table, features, version, "; ".join(notes), args.results)
    print(f"Wrote {written} result rows to {args.results}")
    return 0


def _run(
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
        for model in ("majority", "logistic_regression"):
            scores = _score(train, test, features, model)
            result_rows.append(
                _record(
                    created, version, people, features, model, held_out, scores, note
                )
            )
            _print_fold(model, held_out, scores)
    result_rows.extend(_means(result_rows, created, version, people, features, note))
    _append(destination, result_rows)
    return len(result_rows)


def _score(
    train: list[dict[str, str]],
    test: list[dict[str, str]],
    features: list[str],
    model: str,
) -> dict[str, float | int]:
    y_train = [row["label"] for row in train]
    y_test = [row["label"] for row in test]
    if model == "majority":
        guess = Counter(y_train).most_common(1)[0][0]
        predicted = [guess] * len(y_test)
    else:
        scaler = StandardScaler()
        x_train = scaler.fit_transform(_matrix(train, features))
        x_test = scaler.transform(_matrix(test, features))
        # The name says regression. The decision is a class.
        fitted = LogisticRegression(max_iter=1000, random_state=0)
        fitted.fit(x_train, y_train)
        predicted = fitted.predict(x_test).tolist()
    per_class = f1_score(
        y_test,
        predicted,
        labels=list(POSTURE_LABELS),
        average=None,
        zero_division=0,
    )
    macro = f1_score(
        y_test,
        predicted,
        labels=list(POSTURE_LABELS),
        average="macro",
        zero_division=0,
    )
    scores: dict[str, float | int] = {
        "n_train": len(train),
        "n_test": len(test),
        "macro_f1": float(macro),
    }
    for label, value in zip(POSTURE_LABELS, per_class, strict=True):
        scores[f"f1_{label}"] = float(value)
    return scores


def _means(
    fold_rows: list[dict[str, str]],
    created: str,
    version: str,
    people: str,
    features: list[str],
    note: str,
) -> list[dict[str, str]]:
    means: list[dict[str, str]] = []
    models = sorted({row["model"] for row in fold_rows})
    for model in models:
        group = [row for row in fold_rows if row["model"] == model]
        averaged = {
            key: sum(float(row[key]) for row in group) / len(group)
            for key in (
                "n_train",
                "n_test",
                "macro_f1",
                "f1_dik",
                "f1_one_egik",
                "f1_kambur",
                "f1_yana_yatik",
            )
        }
        means.append(
            _record(
                created,
                version,
                people,
                features,
                model,
                "mean",
                averaged,
                note + "; mean of the person folds; pipeline check, not a performance claim",
            )
        )
        print(
            f"{model} mean macro F1 {averaged['macro_f1']:.3f} "
            "(two people, pipeline check)"
        )
    return means


def _record(
    created: str,
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
        "task": "posture",
        "data_version": version,
        "people": people,
        "features": ",".join(features),
        "model": model,
        "held_out": held_out,
        "note": note,
    }
    for key, value in scores.items():
        if key in {"n_train", "n_test"}:
            row[key] = str(int(round(float(value))))
        else:
            row[key] = f"{float(value):.4f}"
    return row


def _append(destination: Path, rows: list[dict[str, str]]) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    write_header = not destination.exists() or destination.stat().st_size == 0
    with destination.open("a", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        if write_header:
            writer.writeheader()
        writer.writerows(rows)


def _matrix(rows: list[dict[str, str]], features: list[str]) -> list[list[float]]:
    return [[float(row[feature]) for feature in features] for row in rows]


def _print_plan(
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


def _print_fold(model: str, held_out: str, scores: dict[str, float | int]) -> None:
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
