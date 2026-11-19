"""Phase 4: calibration, uncertainty quantification, robustness and error analysis."""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.base import clone
from sklearn.metrics import (
    accuracy_score, balanced_accuracy_score, brier_score_loss,
    f1_score, log_loss, precision_score, recall_score, roc_auc_score,
)
from sklearn.model_selection import (
    RepeatedStratifiedKFold, StratifiedKFold, cross_validate,
    train_test_split,
)

from .data import LEAKAGE_COLUMNS, TARGET_COLUMN
from .modeling import RANDOM_STATE, build_models


POSITIVE_THRESHOLD = 0.50
CALIBRATION_BINS = 8


def calibration_bins(y_true, probabilities, n_bins: int = CALIBRATION_BINS) -> list[dict]:
    """Return equal-width reliability bins; empty bins are omitted."""
    y = np.asarray(y_true, dtype=int)
    p = np.asarray(probabilities, dtype=float)
    if len(y) != len(p) or len(y) == 0:
        raise ValueError("y_true and probabilities must be non-empty and equally sized.")
    if np.any((p < 0) | (p > 1)):
        raise ValueError("Probabilities must be between 0 and 1.")
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    rows = []
    for index in range(n_bins):
        mask = (p >= edges[index]) & (
            (p < edges[index + 1]) if index < n_bins - 1 else (p <= edges[index + 1])
        )
        if mask.any():
            rows.append({
                "bin": int(index + 1),
                "lower_bound": float(edges[index]),
                "upper_bound": float(edges[index + 1]),
                "count": int(mask.sum()),
                "mean_predicted_probability": float(p[mask].mean()),
                "observed_positive_rate": float(y[mask].mean()),
            })
    return rows


def expected_calibration_error(y_true, probabilities, n_bins: int = CALIBRATION_BINS) -> float:
    """Compute a simple count-weighted expected calibration error."""
    rows = calibration_bins(y_true, probabilities, n_bins=n_bins)
    total = sum(row["count"] for row in rows)
    return float(sum(
        row["count"] / total * abs(
            row["observed_positive_rate"] - row["mean_predicted_probability"]
        ) for row in rows
    ))


def _metric_values(y_true, probabilities, threshold: float = POSITIVE_THRESHOLD) -> dict:
    y = np.asarray(y_true, dtype=int)
    p = np.asarray(probabilities, dtype=float)
    pred = (p >= threshold).astype(int)
    result = {
        "accuracy": float(accuracy_score(y, pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y, pred)),
        "precision": float(precision_score(y, pred, zero_division=0)),
        "recall": float(recall_score(y, pred, zero_division=0)),
        "f1": float(f1_score(y, pred, zero_division=0)),
        "brier_score": float(brier_score_loss(y, p)),
        "log_loss": float(log_loss(y, np.clip(p, 1e-7, 1 - 1e-7), labels=[0, 1])),
        "expected_calibration_error": expected_calibration_error(y, p),
    }
    if np.unique(y).size == 2:
        result["roc_auc"] = float(roc_auc_score(y, p))
    else:
        result["roc_auc"] = None
    return result


def bootstrap_confidence_intervals(
    y_true, probabilities, repeats: int = 1000, confidence: float = 0.95,
    random_state: int = RANDOM_STATE,
) -> dict:
    """Percentile bootstrap intervals on the held-out test predictions."""
    y = np.asarray(y_true, dtype=int)
    p = np.asarray(probabilities, dtype=float)
    if len(y) != len(p) or len(y) < 2:
        raise ValueError("At least two paired observations are required.")
    if repeats < 100:
        raise ValueError("Use at least 100 bootstrap repetitions.")
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between 0 and 1.")
    rng = np.random.default_rng(random_state)
    names = [
        "accuracy", "balanced_accuracy", "precision", "recall", "f1",
        "brier_score", "log_loss", "expected_calibration_error", "roc_auc",
    ]
    samples = {name: [] for name in names}
    for _ in range(repeats):
        indices = rng.integers(0, len(y), size=len(y))
        if np.unique(y[indices]).size < 2:
            continue
        values = _metric_values(y[indices], p[indices])
        for name in names:
            value = values.get(name)
            if value is not None and np.isfinite(value):
                samples[name].append(float(value))
    alpha = (1.0 - confidence) / 2.0
    intervals = {}
    for name, values in samples.items():
        if values:
            intervals[name] = {
                "lower": float(np.quantile(values, alpha)),
                "upper": float(np.quantile(values, 1 - alpha)),
                "valid_bootstrap_samples": int(len(values)),
            }
    return {
        "method": "Non-parametric percentile bootstrap over held-out predictions",
        "confidence_level": float(confidence),
        "requested_repeats": int(repeats),
        "valid_repeats": int(max((v["valid_bootstrap_samples"] for v in intervals.values()), default=0)),
        "intervals": intervals,
        "warning": "Intervals may be wide and unstable because the held-out sample is small; they quantify test-sample uncertainty, not external validity.",
    }


def _error_group_audit(X_test: pd.DataFrame, y_true, predictions) -> dict:
    y = np.asarray(y_true, dtype=int)
    pred = np.asarray(predictions, dtype=int)
    errors = (y != pred).astype(int)
    output = {}
    for column in ["sex", "school", "address"]:
        if column not in X_test.columns:
            continue
        rows = []
        values = X_test[column].fillna("Missing").astype(str).to_numpy()
        for value in sorted(set(values)):
            mask = values == value
            if not mask.any():
                continue
            rows.append({
                "group": str(value),
                "n": int(mask.sum()),
                "error_count": int(errors[mask].sum()),
                "error_rate": float(errors[mask].mean()),
                "false_positive_count": int(((pred == 1) & (y == 0) & mask).sum()),
                "false_negative_count": int(((pred == 0) & (y == 1) & mask).sum()),
                "observed_positive_rate": float(y[mask].mean()),
            })
        output[column] = rows
    return output


def _robustness_comparison(X_train, y_train, repeats: int = 3) -> list[dict]:
    """Training-partition repeated CV variability for each fixed baseline family."""
    cv = RepeatedStratifiedKFold(
        n_splits=5, n_repeats=repeats, random_state=RANDOM_STATE
    )
    scoring = {"f1": "f1", "balanced_accuracy": "balanced_accuracy"}
    rows = []
    for name, estimator in build_models(X_train).items():
        scores = cross_validate(
            estimator, X_train, y_train, cv=cv, scoring=scoring,
            n_jobs=1, error_score="raise",
        )
        rows.append({
            "model": name,
            "folds": int(5 * repeats),
            "f1_mean": float(np.mean(scores["test_f1"])),
            "f1_std": float(np.std(scores["test_f1"], ddof=1)),
            "balanced_accuracy_mean": float(np.mean(scores["test_balanced_accuracy"])),
            "balanced_accuracy_std": float(np.std(scores["test_balanced_accuracy"], ddof=1)),
        })
    return rows


def run_phase4_analysis(
    frame: pd.DataFrame, bootstrap_repeats: int = 1000,
    robustness_repeats: int = 3,
) -> dict:
    """Run a pre-specified Phase 4 analysis without test-set model tuning."""
    if TARGET_COLUMN not in frame:
        raise ValueError(f"Required target column {TARGET_COLUMN!r} is missing.")
    X = frame.drop(columns=[c for c in LEAKAGE_COLUMNS if c in frame.columns]).copy()
    if X.empty:
        raise ValueError("No predictors remain after excluding G1, G2 and G3.")
    y = (frame[TARGET_COLUMN] < 10).astype(int)
    if y.nunique() != 2 or int(y.value_counts().min()) < 5:
        raise ValueError("The target needs at least five observations in each class.")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=RANDOM_STATE, stratify=y
    )
    # Five-fold CV needs at least five examples from each class in the
    # training partition; checking the original dataset alone is insufficient.
    minimum_training_class_count = int(y_train.value_counts().min())
    if minimum_training_class_count < 5:
        raise ValueError(
            "After the stratified 75/25 split, each training class must contain "
            "at least five observations for 5-fold cross-validation. "
            "Provide a larger dataset or use a separately pre-specified design."
        )

    # Baseline selection uses training-only CV.
    selection_cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    candidates = []
    for name, estimator in build_models(X_train).items():
        scores = cross_validate(
            estimator, X_train, y_train, cv=selection_cv,
            scoring={"f1": "f1", "balanced_accuracy": "balanced_accuracy"},
            n_jobs=1, error_score="raise",
        )
        candidates.append((
            float(np.mean(scores["test_f1"])),
            float(np.mean(scores["test_balanced_accuracy"])),
            name, estimator,
        ))
    candidates.sort(key=lambda row: (row[0], row[1]), reverse=True)
    cv_f1, cv_balanced, selected_name, selected_estimator = candidates[0]

    raw_model = clone(selected_estimator).fit(X_train, y_train)
    raw_probabilities = raw_model.predict_proba(X_test)[:, 1]

    # Sigmoid calibration is pre-specified; it is not selected by test-set performance.
    calibration_cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE + 1)
    calibrated_model = CalibratedClassifierCV(
        estimator=clone(selected_estimator), method="sigmoid", cv=calibration_cv,
    )
    calibrated_model.fit(X_train, y_train)
    calibrated_probabilities = calibrated_model.predict_proba(X_test)[:, 1]
    predictions = (calibrated_probabilities >= POSITIVE_THRESHOLD).astype(int)

    raw_metrics = _metric_values(y_test, raw_probabilities)
    calibrated_metrics = _metric_values(y_test, calibrated_probabilities)
    confusion = {
        "true_negative": int(((y_test.to_numpy() == 0) & (predictions == 0)).sum()),
        "false_positive": int(((y_test.to_numpy() == 0) & (predictions == 1)).sum()),
        "false_negative": int(((y_test.to_numpy() == 1) & (predictions == 0)).sum()),
        "true_positive": int(((y_test.to_numpy() == 1) & (predictions == 1)).sum()),
    }
    error_summary = {
        "test_records": int(len(y_test)),
        "errors": int((y_test.to_numpy() != predictions).sum()),
        "error_rate": float((y_test.to_numpy() != predictions).mean()),
        "false_positives": confusion["false_positive"],
        "false_negatives": confusion["false_negative"],
        "confusion_counts": confusion,
        "group_diagnostics": _error_group_audit(X_test, y_test, predictions),
    }

    return {
        "dataset": "UCI Student Performance — Mathematics cohort",
        "target": "G3 < 10 on the original 0–20 grade scale",
        "selected_model": selected_name,
        "training_cv_selection": {
            "mean_f1": cv_f1,
            "mean_balanced_accuracy": cv_balanced,
            "selection_data": "Training partition only",
        },
        "sample_sizes": {
            "total": int(len(frame)),
            "training": int(len(X_train)),
            "held_out_test": int(len(X_test)),
        },
        "probability_calibration": {
            "method": "Sigmoid (Platt-style) calibration fitted with 5-fold CV on training data",
            "decision_threshold": POSITIVE_THRESHOLD,
            "raw_metrics": raw_metrics,
            "calibrated_metrics": calibrated_metrics,
            "raw_reliability_bins": calibration_bins(y_test, raw_probabilities),
            "calibrated_reliability_bins": calibration_bins(y_test, calibrated_probabilities),
            "interpretation": "Compare Brier score, log loss and reliability bins. Calibration does not guarantee accurate individual probabilities.",
        },
        "uncertainty": {
            "raw_model": bootstrap_confidence_intervals(
                y_test, raw_probabilities, repeats=bootstrap_repeats,
                random_state=RANDOM_STATE,
            ),
            "calibrated_model": bootstrap_confidence_intervals(
                y_test, calibrated_probabilities, repeats=bootstrap_repeats,
                random_state=RANDOM_STATE + 1,
            ),
        },
        "error_analysis": error_summary,
        "robustness": {
            "method": f"Repeated stratified 5-fold CV ({robustness_repeats} repeats) on training partition",
            "results": _robustness_comparison(X_train, y_train, repeats=robustness_repeats),
            "warning": "These are training-partition stability diagnostics, not an independent final performance estimate.",
        },
        "methodology": {
            "split": "Stratified 75/25 train/test, random_state=42",
            "predictors": "All available columns except G1, G2 and G3",
            "predictor_columns": X.columns.tolist(),
            "excluded_columns": [column for column in LEAKAGE_COLUMNS if column in frame.columns],
            "model_selection": "Training-only stratified 5-fold CV; mean F1, balanced accuracy tie-breaker",
            "calibration": "Pre-specified sigmoid calibration using 5-fold CV within training data",
            "test_policy": "Held-out test data is used once for final raw and calibrated evaluation; no threshold or model selection on test data",
            "bootstrap": f"{bootstrap_repeats} percentile-bootstrap resamples of held-out predictions",
            "decision_threshold": POSITIVE_THRESHOLD,
            "random_state": RANDOM_STATE,
            "minimum_training_class_count": minimum_training_class_count,
        },
        "limitations": [
            "The dataset represents two Portuguese secondary schools and is not representative of Pakistani learners.",
            "The held-out test sample is small; bootstrap intervals can be unstable.",
            "Calibration is a population-level diagnostic and does not make an individual prediction certain.",
            "Repeated CV results describe training-partition variability, not external generalisation.",
            "Group error comparisons are descriptive and may be unstable for small groups.",
            "This research prototype must never be used to rank, diagnose, punish, admit, exclude, or deny support to learners.",
        ],
    }
