"""Leave-one-subject-out. A person's rows stay entirely on one side of the split."""

from __future__ import annotations


def loso(rows: list[dict[str, str]]) -> list[tuple[str, list[dict[str, str]], list[dict[str, str]]]]:
    people = sorted({row["person_code"] for row in rows})
    folds: list[tuple[str, list[dict[str, str]], list[dict[str, str]]]] = []
    for held_out in people:
        train = [row for row in rows if row["person_code"] != held_out]
        test = [row for row in rows if row["person_code"] == held_out]
        if not train or not test:
            raise ValueError(f"Empty split when holding out {held_out}")
        folds.append((held_out, train, test))
    return folds
