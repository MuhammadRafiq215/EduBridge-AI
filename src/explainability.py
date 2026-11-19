"""Phase 5: model-agnostic SHAP explanations for the research prototype."""
from __future__ import annotations

import numpy as np
import pandas as pd
import shap
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split

from .data import LEAKAGE_COLUMNS, TARGET_COLUMN
from .modeling import RANDOM_STATE, build_models


def summarize_shap_values(values, feature_names: list[str]) -> pd.DataFrame:
    """Summarize mean absolute and signed SHAP contributions by feature."""
    matrix = np.asarray(values, dtype=float)
    if matrix.ndim != 2 or matrix.shape[1] != len(feature_names):
        raise ValueError("SHAP values must be a 2D matrix aligned with feature_names.")
    if matrix.shape[0] == 0 or not np.isfinite(matrix).all():
        raise ValueError("SHAP values must contain finite observations.")
    summary = pd.DataFrame({
        "feature": feature_names,
        "mean_abs_shap": np.mean(np.abs(matrix), axis=0),
        "mean_shap": np.mean(matrix, axis=0),
    })
    return summary.sort_values("mean_abs_shap", ascending=False).reset_index(drop=True)


def run_phase5_explanations(
    frame: pd.DataFrame,
    background_size: int = 40,
    explain_size: int = 25,
) -> dict:
    """Fit a training-only baseline and explain a small held-out sample with SHAP."""
    if TARGET_COLUMN not in frame.columns:
        raise ValueError(f"Required target column {TARGET_COLUMN!r} is missing.")
    X = frame.drop(columns=[column for column in LEAKAGE_COLUMNS if column in frame.columns]).copy()
    if X.empty:
        raise ValueError("No predictors remain after excluding G1, G2 and G3.")
    y = (frame[TARGET_COLUMN] < 10).astype(int)
    if y.nunique() != 2 or int(y.value_counts().min()) < 5:
        raise ValueError("The target needs at least five observations in each class.")
    if background_size < 5 or explain_size < 1:
        raise ValueError("Use at least five background rows and one explanation row.")

    X_train, X_test, y_train, _ = train_test_split(
        X, y, test_size=0.25, random_state=RANDOM_STATE, stratify=y
    )
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    candidates = []
    for name, estimator in build_models(X_train).items():
        scores = cross_validate(
            estimator, X_train, y_train, cv=cv,
            scoring={"f1": "f1", "balanced_accuracy": "balanced_accuracy"},
            n_jobs=1, error_score="raise",
        )
        candidates.append((
            float(np.mean(scores["test_f1"])),
            float(np.mean(scores["test_balanced_accuracy"])),
            name,
            estimator,
        ))
    candidates.sort(key=lambda item: (item[0], item[1]), reverse=True)
    cv_f1, cv_balanced_accuracy, selected_name, selected_estimator = candidates[0]
    model = selected_estimator.fit(X_train, y_train)

    feature_names = X.columns.tolist()
    background = X_train.sample(
        n=min(int(background_size), len(X_train)), random_state=RANDOM_STATE
    )
    explained = X_test.sample(
        n=min(int(explain_size), len(X_test)), random_state=RANDOM_STATE
    )

    def predict_positive(values):
        array = np.asarray(values, dtype=object)
        if array.ndim == 1:
            array = array.reshape(1, -1)
        batch = pd.DataFrame(array, columns=feature_names)
        return model.predict_proba(batch)[:, 1]

    masker = shap.maskers.Independent(background, max_samples=len(background))
    explainer = shap.PermutationExplainer(
        predict_positive, masker, feature_names=feature_names, seed=RANDOM_STATE
    )
    max_evaluations = max(2 * len(feature_names) + 1, 100)
    explanation = explainer(
        explained, max_evals=max_evaluations, batch_size="auto"
    )
    values = np.asarray(explanation.values, dtype=float)
    if values.ndim == 3 and values.shape[-1] == 1:
        values = values[:, :, 0]
    if values.ndim != 2:
        raise ValueError(f"Unexpected SHAP output shape: {values.shape}")

    summary = summarize_shap_values(values, feature_names)
    probabilities = predict_positive(explained.to_numpy(dtype=object))
    base_values = np.asarray(explanation.base_values, dtype=float).reshape(-1)
    if len(base_values) == 1 and len(explained) > 1:
        base_values = np.repeat(base_values, len(explained))

    return {
        "dataset": "UCI Student Performance — Mathematics cohort",
        "selected_model": selected_name,
        "training_cv": {
            "mean_f1": cv_f1,
            "mean_balanced_accuracy": cv_balanced_accuracy,
            "selection_data": "Training partition only",
        },
        "sample_sizes": {
            "training": int(len(X_train)),
            "held_out_explained": int(len(explained)),
            "background": int(len(background)),
        },
        "feature_names": feature_names,
        "shap_values": values.tolist(),
        "base_values": base_values.tolist(),
        "predicted_probabilities": probabilities.tolist(),
        "explained_rows": explained.astype(object).where(pd.notna(explained), None).to_dict(orient="records"),
        "global_summary": summary.to_dict(orient="records"),
        "method": (
            "Model-agnostic SHAP PermutationExplainer; model selected using "
            "training-only stratified 5-fold CV; background sampled from training data; "
            "explanations generated on a held-out sample."
        ),
        "limitations": [
            "SHAP values describe how this fitted model allocates its prediction relative to the selected background; they do not establish causation.",
            "Correlated features can share or redistribute attribution, so rankings are not unique causal effects.",
            "The background and explanation samples are small computational samples from this dataset.",
            "The source dataset represents two Portuguese schools and is not validated for Pakistani learners.",
            "This research prototype must never be used to rank, diagnose, punish, admit, exclude, or deny support to learners.",
        ],
    }
