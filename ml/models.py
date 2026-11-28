"""Estimators compared by SW-076. Every model sees the same training rows."""

from __future__ import annotations

import os
import warnings
from collections import Counter

# Joblib warns when it cannot count physical cores. One thread is enough here.
os.environ.setdefault("LOKY_MAX_CPU_COUNT", "1")

import numpy as np
from lightgbm import LGBMClassifier, LGBMRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.preprocessing import StandardScaler

from ml.rules import predict_posture_rule

POSTURE_MODELS = (
    "majority",
    "rule",
    "logistic_regression",
    "random_forest",
    "lightgbm",
)
DISTANCE_MODELS = (
    "rule",
    "linear_regression",
    "random_forest",
    "lightgbm",
)


def predict_posture(
    train: list[dict[str, str]],
    test: list[dict[str, str]],
    features: list[str],
    model: str,
) -> list[str]:
    if model == "majority":
        guess = Counter(row["label"] for row in train).most_common(1)[0][0]
        return [guess] * len(test)
    if model == "rule":
        return predict_posture_rule(train, test)
    y_train = [row["label"] for row in train]
    x_train = _matrix(train, features)
    x_test = _matrix(test, features)
    if model == "logistic_regression":
        # A straight boundary. Scale so a ratio and a tilt share one weight scale.
        scaler = StandardScaler()
        fitted = LogisticRegression(max_iter=1000, random_state=0)
        fitted.fit(scaler.fit_transform(x_train), y_train)
        return [str(label) for label in _predict(fitted, scaler.transform(x_test))]
    if model == "random_forest":
        fitted_forest = RandomForestClassifier(
            n_estimators=200, random_state=0, n_jobs=1
        )
        fitted_forest.fit(x_train, y_train)
        return [str(label) for label in _predict(fitted_forest, x_test)]
    if model == "lightgbm":
        fitted_boost = LGBMClassifier(
            n_estimators=100,
            learning_rate=0.1,
            random_state=0,
            n_jobs=1,
            verbosity=-1,
            force_col_wise=True,
        )
        fitted_boost.fit(x_train, y_train)
        return [str(label) for label in _predict(fitted_boost, x_test)]
    raise ValueError(f"Unknown posture model {model}")


def predict_distance(
    train: list[dict[str, str]],
    test: list[dict[str, str]],
    model: str,
) -> list[float]:
    """Correct the iris centimetres toward the ruler. The rule leaves them as read."""
    if model == "rule":
        return [float(row["distanceCm"]) for row in test]
    y_train = [float(row["distance_cm"]) for row in train]
    x_train = _matrix(train, ["distanceCm"])
    x_test = _matrix(test, ["distanceCm"])
    if model == "linear_regression":
        fitted_line = LinearRegression()
        fitted_line.fit(x_train, y_train)
        return [float(value) for value in _predict(fitted_line, x_test)]
    if model == "random_forest":
        fitted_forest = RandomForestRegressor(
            n_estimators=200, random_state=0, n_jobs=1
        )
        fitted_forest.fit(x_train, y_train)
        return [float(value) for value in _predict(fitted_forest, x_test)]
    if model == "lightgbm":
        fitted_boost = LGBMRegressor(
            n_estimators=100,
            learning_rate=0.1,
            random_state=0,
            n_jobs=1,
            verbosity=-1,
            force_col_wise=True,
        )
        fitted_boost.fit(x_train, y_train)
        return [float(value) for value in _predict(fitted_boost, x_test)]
    raise ValueError(f"Unknown distance model {model}")


def _predict(fitted, x_test: np.ndarray) -> np.ndarray:
    # LightGBM names the columns itself, then warns that the next array has none.
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="X does not have valid feature names",
            category=UserWarning,
        )
        return fitted.predict(x_test)


def _matrix(rows: list[dict[str, str]], features: list[str]) -> np.ndarray:
    # A plain array, so fit and predict do not invent column names.
    return np.asarray(
        [[float(row[feature]) for feature in features] for row in rows],
        dtype=float,
    )
