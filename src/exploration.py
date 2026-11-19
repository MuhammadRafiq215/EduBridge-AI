"""Phase 3: exploratory analysis and target-definition sensitivity."""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import (
    balanced_accuracy_score, f1_score, precision_score, recall_score,
)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split

from .data import LEAKAGE_COLUMNS, TARGET_COLUMN
from .modeling import RANDOM_STATE, build_models


TARGET_THRESHOLDS = (8, 10, 12)


def exploratory_summary(frame: pd.DataFrame) -> dict:
    """Create descriptive summaries without using grades as model predictors."""
    if TARGET_COLUMN not in frame:
        raise ValueError(f"Required target column {TARGET_COLUMN!r} is missing.")
    numeric = frame.select_dtypes(include=["number", "bool"])
    grade_counts = (
        frame[TARGET_COLUMN].value_counts().sort_index().rename_axis("grade")
        .reset_index(name="count")
    )
    grade_counts["grade"] = grade_counts["grade"].astype(int)
    numeric_summary = numeric.describe().replace({np.nan: None}).round(3)
    correlations = numeric.corr(numeric_only=True)[TARGET_COLUMN].drop(TARGET_COLUMN)
    correlations = correlations.reindex(correlations.abs().sort_values(ascending=False).index)
    categorical = {}
    for column in frame.select_dtypes(exclude=["number", "bool"]).columns:
        counts = frame[column].fillna("Missing").astype(str).value_counts()
        categorical[column] = [
            {"category": str(key), "count": int(value),
             "share": float(value / len(frame))}
            for key, value in counts.items()
        ]
    return {
        "rows": int(len(frame)),
        "grade_counts": grade_counts.to_dict(orient="records"),
        "numeric_summary": [
            {"feature": str(index), **{
                str(k): (None if pd.isna(v) else float(v))
                for k, v in row.items()
            }}
            for index, row in numeric_summary.iterrows()
        ],
        "grade_correlations": [
            {"feature": str(index), "correlation_with_G3": float(value)}
            for index, value in correlations.items() if pd.notna(value)
        ],
        "categorical_distributions": categorical,
    }


def target_sensitivity(
    frame: pd.DataFrame,
    thresholds: tuple[int, ...] = TARGET_THRESHOLDS,
) -> list[dict]:
    """Re-run model selection for each G3 cut-off on one fixed stratified split.

    Each row is a separate research definition: positive means G3 < cutoff.
    The same predictor policy, split seed, CV design and model family are used.
    No threshold is selected as a policy recommendation.
    """
    if TARGET_COLUMN not in frame:
        raise ValueError(f"Required target column {TARGET_COLUMN!r} is missing.")
    X = frame.drop(columns=[c for c in LEAKAGE_COLUMNS if c in frame.columns]).copy()
    if X.empty:
        raise ValueError("No predictors remain after excluding G1, G2 and G3.")
    output = []
    for cutoff in thresholds:
        y = (frame[TARGET_COLUMN] < cutoff).astype(int)
        counts = y.value_counts()
        if y.nunique() != 2 or int(counts.min()) < 5:
            output.append({
                "cutoff": int(cutoff), "definition": f"G3 < {cutoff}",
                "status": "insufficient_class_support",
                "positive_count": int(y.sum()),
                "negative_count": int((1 - y).sum()),
                "positive_rate": float(y.mean()),
            })
            continue
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.25, random_state=RANDOM_STATE, stratify=y
        )
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
        scores = {"f1": "f1", "balanced_accuracy": "balanced_accuracy"}
        candidates = []
        for name, estimator in build_models(X_train).items():
            cv_result = cross_validate(
                estimator, X_train, y_train, cv=cv, scoring=scores,
                n_jobs=1, error_score="raise",
            )
            candidates.append((
                float(np.mean(cv_result["test_f1"])),
                float(np.mean(cv_result["test_balanced_accuracy"])),
                name, estimator,
            ))
        candidates.sort(key=lambda item: (item[0], item[1]), reverse=True)
        cv_f1, cv_balanced, selected_name, selected = candidates[0]
        selected.fit(X_train, y_train)
        probability = selected.predict_proba(X_test)[:, 1]
        prediction = (probability >= 0.5).astype(int)
        output.append({
            "cutoff": int(cutoff),
            "definition": f"G3 < {cutoff}",
            "status": "evaluated",
            "positive_count": int(y.sum()),
            "negative_count": int((1 - y).sum()),
            "positive_rate": float(y.mean()),
            "test_positive_rate": float(y_test.mean()),
            "selected_model": selected_name,
            "cv_f1": cv_f1,
            "cv_balanced_accuracy": cv_balanced,
            "test_precision": float(precision_score(y_test, prediction, zero_division=0)),
            "test_recall": float(recall_score(y_test, prediction, zero_division=0)),
            "test_f1": float(f1_score(y_test, prediction, zero_division=0)),
            "test_balanced_accuracy": float(balanced_accuracy_score(y_test, prediction)),
            "test_predicted_positive_rate": float(prediction.mean()),
        })
    return output


def run_phase3_analysis(frame: pd.DataFrame) -> dict:
    """Run all Phase 3 descriptive and target sensitivity analyses."""
    return {
        "exploratory": exploratory_summary(frame),
        "target_sensitivity": target_sensitivity(frame),
        "methodology": {
            "grade_scale": "Original UCI final grade G3, 0–20",
            "definitions": ["G3 < 8", "G3 < 10", "G3 < 12"],
            "predictors": "All available columns except G1, G2 and G3",
            "split": "Same 75/25 stratified split seed (42) for each definition",
            "selection": "Separate model selection per target using stratified 5-fold training CV F1; balanced accuracy tie-breaker",
            "test_threshold": "Predicted positive when probability >= 0.50",
            "interpretation": "Sensitivity analysis only; no cut-off is selected as a recommended student label or intervention policy",
        },
    }
