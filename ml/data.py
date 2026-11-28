"""Load SitWise-Desk CSVs. The files stay in a folder outside the repository."""

from __future__ import annotations

import csv
import hashlib
import re
from pathlib import Path

# Commanded postures. The other labels belong to other jobs.
POSTURE_LABELS = ("dik", "one_egik", "kambur", "yana_yatik")

# Landmark ratios. A column joins this run only when every person has values.
POSTURE_FEATURES = ("neckRatio", "shoulderTilt", "noseShoulderDrop")

# Present in the file, and deliberately not a posture input.
# distanceCm is the iris estimate. distance_cm is the ruler answer.
HELD_BACK = (
    "distanceCm",
    "distance_cm",
    "earShoulderDrop",
    "headPitch",
    "EAR",
    "blinksPerMinute",
    "PERCLOS",
    "MAR",
    "headDrop",
)

EXCLUDED_LABELS = {
    "kalibrasyon": "five-second reference sit, not one of the four posture classes",
    "mesafe_cm": "distance task; the ruler column is the answer, not a posture class",
    "serbest": "no commanded posture",
}

REQUIRED = ("person_code", "session", "label", *POSTURE_FEATURES)
RULER_CM = (40, 60, 80)
_PERSON_CODE = re.compile(r"P\d+")
_SESSION_DATE = re.compile(r"(\d{4}-\d{2}-\d{2})")


def load_directory(directory: Path) -> tuple[list[dict[str, str]], str]:
    files = sorted(path for path in directory.glob("*.csv") if path.is_file())
    if not files:
        raise ValueError(f"No CSV files in {directory}")
    return load_files(files)


def latest_session_files(directory: Path) -> tuple[list[Path], list[str]]:
    """Keep one file per person. A later sitting replaces an earlier one.

    Two files with the same person code would be one subject counted twice.
    The date in the file name decides which sitting stays.
    """
    files = sorted(path for path in directory.glob("*.csv") if path.is_file())
    if not files:
        raise ValueError(f"No CSV files in {directory}")
    groups: dict[str, list[Path]] = {}
    for path in files:
        code = path.name.split("_", 1)[0]
        groups.setdefault(code, []).append(path)
    chosen: list[Path] = []
    notes: list[str] = []
    for code in sorted(groups):
        paths = groups[code]
        if len(paths) == 1:
            chosen.append(paths[0])
            continue
        ranked = sorted(paths, key=_session_key)
        keep = ranked[-1]
        chosen.append(keep)
        skipped = ", ".join(_logged_name(path) for path in ranked[:-1])
        notes.append(f"{code}: kept {_logged_name(keep)}; skipped {skipped}")
    return sorted(chosen, key=lambda path: path.name), notes


def load_files(files: list[Path]) -> tuple[list[dict[str, str]], str]:
    if not files:
        raise ValueError("No CSV files to load")
    rows: list[dict[str, str]] = []
    version_parts: list[str] = []
    for path in files:
        file_rows = _read_csv(path)
        _reject_images(path, file_rows)
        code = _person_code(path, file_rows)
        rows.extend(file_rows)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()[:12]
        version_parts.append(f"{code}:{_logged_name(path)}:{digest}")
    return rows, "+".join(version_parts)


def distance_table(
    rows: list[dict[str, str]],
) -> tuple[list[dict[str, str]], list[str], list[str]]:
    """Ruler rows only. The answer is distance_cm. The input is distanceCm."""
    people = {row["person_code"] for row in rows}
    if len(people) < 2:
        found = ", ".join(sorted(people)) or "none"
        raise ValueError(
            "Leave-one-subject-out needs two person codes. "
            f"This folder has {found}. One person cannot be both the training "
            "set and the test set."
        )
    kept: list[dict[str, str]] = []
    empty = 0
    rejected = 0
    for row in rows:
        if row["label"] != "mesafe_cm":
            continue
        iris = row.get("distanceCm", "").strip()
        ruler = row.get("distance_cm", "").strip()
        if not iris or not ruler:
            empty += 1
            continue
        try:
            iris_value = float(iris)
            ruler_value = float(ruler)
        except ValueError:
            rejected += 1
            continue
        if ruler_value not in RULER_CM or iris_value <= 0:
            rejected += 1
            continue
        kept.append(row)
    if not kept:
        raise ValueError("No distance rows with a ruler value of 40, 60 or 80 cm.")
    if len({row["person_code"] for row in kept}) < 2:
        raise ValueError("Distance rows belong to fewer than two people.")
    notes = [
        "distance rows are the ruler step only; "
        "distance_cm is the answer and distanceCm is the iris estimate"
    ]
    if empty:
        notes.append(f"{empty} distance rows dropped because iris or ruler was empty")
    if rejected:
        notes.append(
            f"{rejected} distance rows dropped because the ruler was not 40, 60 or 80"
        )
    return kept, ["distanceCm"], notes


def _logged_name(path: Path) -> str:
    """The result log keeps the person code and the date, not a local nickname."""
    return re.sub(r"\([^)]*\)", "", path.name)


def _session_key(path: Path) -> tuple[str, str]:
    match = _SESSION_DATE.search(path.name)
    if match is None:
        raise ValueError(f"{path.name} has no session date in the file name")
    return match.group(1), path.name


def posture_table(
    rows: list[dict[str, str]],
) -> tuple[list[dict[str, str]], list[str], list[str]]:
    """Return posture rows, the features both people have, and skip notes."""
    people = {row["person_code"] for row in rows}
    if len(people) < 2:
        found = ", ".join(sorted(people)) or "none"
        raise ValueError(
            "Leave-one-subject-out needs two person codes. "
            f"This folder has {found}. One person cannot be both the training "
            "set and the test set."
        )
    kept = [row for row in rows if row["label"] in POSTURE_LABELS]
    if not kept:
        raise ValueError("No posture rows. Expected dik, one_egik, kambur, yana_yatik.")
    used: list[str] = []
    notes: list[str] = []
    for feature in POSTURE_FEATURES:
        empty = sorted(
            person
            for person in people
            if all(
                not row[feature].strip() for row in kept if row["person_code"] == person
            )
        )
        if empty:
            notes.append(f"{feature} skipped: empty for {', '.join(empty)}")
            continue
        used.append(feature)
    if not used:
        raise ValueError("No posture feature is filled for every person.")
    complete = [row for row in kept if all(row[feature].strip() for feature in used)]
    dropped = len(kept) - len(complete)
    if dropped:
        notes.append(f"{dropped} posture rows dropped because a used feature was empty")
    notes.append(
        "distanceCm and distance_cm are not posture inputs; "
        "distance is a separate regression task"
    )
    return complete, used, notes


def label_counts(rows: list[dict[str, str]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["label"]] = counts.get(row["label"], 0) + 1
    return counts


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"{path.name} has no header")
        missing = [name for name in REQUIRED if name not in reader.fieldnames]
        if missing:
            raise ValueError(f"{path.name} is missing columns: {', '.join(missing)}")
        loaded: list[dict[str, str]] = []
        for raw in reader:
            row = {
                key: (value if value is not None else "") for key, value in raw.items()
            }
            missing = [name for name in REQUIRED if not row[name].strip()]
            # noseShoulderDrop may be empty. The other required columns may not.
            missing = [name for name in missing if name != "noseShoulderDrop"]
            if missing:
                raise ValueError(f"{path.name} has an empty {', '.join(missing)}")
            loaded.append(row)
        return loaded


def _reject_images(path: Path, rows: list[dict[str, str]]) -> None:
    for row in rows:
        for value in row.values():
            if "\x00" in value or "data:image" in value or len(value) > 500:
                raise ValueError(
                    f"{path.name} contains a cell that is not a short number or label"
                )


def _person_code(path: Path, rows: list[dict[str, str]]) -> str:
    codes = {row["person_code"] for row in rows}
    if len(codes) != 1:
        raise ValueError(f"{path.name} has more than one person_code: {sorted(codes)}")
    code = codes.pop()
    if not _PERSON_CODE.fullmatch(code):
        raise ValueError(f"{path.name} has person_code {code!r}")
    prefix = path.name.split("_", 1)[0]
    if prefix != code:
        raise ValueError(
            f"{path.name} starts with {prefix}, but every row says {code}. "
            "The file name and the person code have to match."
        )
    return code
