"""Leakage-aware baseline modelling and evaluation."""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.metrics import (
    accuracy_score, balanced_accuracy_score, brier_score_loss,
    classification_report, confusion_matrix, f1_score, precision_score,
    recall_score, roc_auc_score, average_precision_score, roc_curve,
)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .data import LEAKAGE_COLUMNS, TARGET_COLUMN, audit_dataset, load_student_math

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
RANDOM_STATE = 42


def build_preprocessor(X: pd.DataFrame) -> ColumnTransformer:
    numeric = X.select_dtypes(include=["number", "bool"]).columns.tolist()
    categorical = [column for column in X.columns if column not in numeric]
    numeric_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])
    categorical_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])
    return ColumnTransformer([
        ("numeric", numeric_pipe, numeric),
        ("categorical", categorical_pipe, categorical),
    ], remainder="drop")


def build_models(X: pd.DataFrame) -> dict:
    return {
        "Dummy baseline": Pipeline([
            ("preprocess", build_preprocessor(X)),
            ("model", DummyClassifier(strategy="prior")),
        ]),
        "Logistic Regression": Pipeline([
            ("preprocess", build_preprocessor(X)),
            ("model", LogisticRegression(max_iter=2000, class_weight="balanced",
                                         random_state=RANDOM_STATE)),
        ]),
        "Random Forest": Pipeline([
            ("preprocess", build_preprocessor(X)),
            ("model", RandomForestClassifier(
                n_estimators=350, min_samples_leaf=2, class_weight="balanced",
                random_state=RANDOM_STATE, n_jobs=-1
            )),
        ]),
        "Extra Trees": Pipeline([
            ("preprocess", build_preprocessor(X)),
            ("model", ExtraTreesClassifier(
                n_estimators=300, min_samples_leaf=2, class_weight="balanced",
                random_state=RANDOM_STATE, n_jobs=-1
            )),
        ]),
        "Gradient Boosting": Pipeline([
            ("preprocess", build_preprocessor(X)),
            ("model", GradientBoostingClassifier(
                n_estimators=100, learning_rate=0.05, max_depth=2,
                random_state=RANDOM_STATE
            )),
        ]),
        "RBF Support Vector Machine": Pipeline([
            ("preprocess", build_preprocessor(X)),
            ("model", SVC(
                C=1.0, kernel="rbf", probability=True,
                class_weight="balanced", random_state=RANDOM_STATE
            )),
        ]),
        "K-Nearest Neighbours": Pipeline([
            ("preprocess", build_preprocessor(X)),
            ("model", KNeighborsClassifier(n_neighbors=7, weights="distance")),
        ]),
    }



def threshold_sensitivity(y_true, probabilities, thresholds=(0.30, 0.40, 0.50, 0.60, 0.70)) -> list[dict]:
    """Summarize classification trade-offs; never select a threshold automatically."""
    rows = []
    y_true = np.asarray(y_true, dtype=int)
    probabilities = np.asarray(probabilities, dtype=float)
    for threshold in thresholds:
        predicted = (probabilities >= threshold).astype(int)
        rows.append({
            "threshold": float(threshold),
            "precision": float(precision_score(y_true, predicted, zero_division=0)),
            "recall": float(recall_score(y_true, predicted, zero_division=0)),
            "f1": float(f1_score(y_true, predicted, zero_division=0)),
            "balanced_accuracy": float(balanced_accuracy_score(y_true, predicted)),
            "predicted_positive_rate": float(predicted.mean()),
        })
    return rows


def run_experiment() -> dict:
    """Download data, train baselines, evaluate once on a held-out test set."""
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    frame = load_student_math()
    audit = audit_dataset(frame)

    # Define the research target: G3 < 10 on the original 0–20 scale.
    # G1 and G2 are excluded because they are earlier grades strongly related to G3.
    y = (frame[TARGET_COLUMN] < 10).astype(int).rename("below_threshold")
    X = frame.drop(columns=LEAKAGE_COLUMNS).copy()
    if X.empty:
        raise ValueError("No predictor columns remain after excluding grade columns.")
    if y.nunique() != 2 or y.value_counts().min() < 5:
        raise ValueError("The target does not contain enough examples in both classes.")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=RANDOM_STATE, stratify=y
    )
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    scoring = {
        "accuracy": "accuracy",
        "balanced_accuracy": "balanced_accuracy",
        "precision": "precision",
        "recall": "recall",
        "f1": "f1",
        "roc_auc": "roc_auc",
    }

    comparison = []
    fitted_models = {}
    for name, estimator in build_models(X_train).items():
        cv_result = cross_validate(
            estimator, X_train, y_train, cv=cv, scoring=scoring,
            return_train_score=False, n_jobs=1, error_score="raise"
        )
        comparison.append({
            "model": name,
            **{f"cv_{metric}_mean": float(np.mean(cv_result[f"test_{metric}"]))
               for metric in scoring},
            **{f"cv_{metric}_std": float(np.std(cv_result[f"test_{metric}"], ddof=1))
               for metric in scoring},
        })
        fitted_models[name] = estimator

    comparison_frame = pd.DataFrame(comparison).sort_values(
        ["cv_f1_mean", "cv_balanced_accuracy_mean"], ascending=False
    )
    selected_name = str(comparison_frame.iloc[0]["model"])
    selected_model = fitted_models[selected_name]
    selected_model.fit(X_train, y_train)

    probabilities = selected_model.predict_proba(X_test)[:, 1]
    predictions = (probabilities >= 0.5).astype(int)
    metrics = {
        "selected_model": selected_name,
        "test_size": int(len(y_test)),
        "train_size": int(len(y_train)),
        "accuracy": float(accuracy_score(y_test, predictions)),
        "balanced_accuracy": float(balanced_accuracy_score(y_test, predictions)),
        "precision": float(precision_score(y_test, predictions, zero_division=0)),
        "recall": float(recall_score(y_test, predictions, zero_division=0)),
        "f1": float(f1_score(y_test, predictions, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, probabilities)),
        "average_precision": float(average_precision_score(y_test, probabilities)),
        "brier_score": float(brier_score_loss(y_test, probabilities)),
        "confusion_matrix": confusion_matrix(y_test, predictions, labels=[0, 1]).tolist(),
        "classification_report": classification_report(
            y_test, predictions, labels=[0, 1],
            target_names=["At or above threshold", "Below threshold"],
            output_dict=True, zero_division=0
        ),
        "roc_curve": {
            "fpr": roc_curve(y_test, probabilities)[0].tolist(),
            "tpr": roc_curve(y_test, probabilities)[1].tolist(),
        },
        "positive_class_definition": "G3 < 10 on the original 0–20 grade scale",
        "decision_threshold": 0.5,
        "threshold_sensitivity": threshold_sensitivity(y_test, probabilities),
        "random_state": RANDOM_STATE,
        "cv_folds": 5,
        "predictor_columns": X.columns.tolist(),
        "excluded_columns": LEAKAGE_COLUMNS,
    }

    # Post-evaluation model inspection on the held-out set; do not use this to tune.
    importance = permutation_importance(
        selected_model, X_test, y_test, scoring="f1",
        n_repeats=20, random_state=RANDOM_STATE, n_jobs=1
    )
    importance_frame = pd.DataFrame({
        "feature": X.columns,
        "importance_mean": importance.importances_mean,
        "importance_std": importance.importances_std,
    }).sort_values("importance_mean", ascending=False)

    # Descriptive group audit only; these small subgroup results are not proof of fairness.
    group_audit = {}
    for group_column in ["sex", "school", "address"]:
        if group_column in X_test.columns:
            group_rows = []
            for group_value in sorted(X_test[group_column].dropna().unique(), key=str):
                mask = X_test[group_column].eq(group_value).to_numpy()
                if int(mask.sum()) == 0:
                    continue
                group_rows.append({
                    "group": str(group_value),
                    "n": int(mask.sum()),
                    "observed_below_threshold_rate": float(y_test.iloc[np.where(mask)[0]].mean()),
                    "predicted_below_threshold_rate": float(predictions[mask].mean()),
                    "recall": float(recall_score(y_test.iloc[np.where(mask)[0]],
                                                 predictions[mask], zero_division=0)),
                })
            group_audit[group_column] = group_rows

    pd.DataFrame(metrics["threshold_sensitivity"]).to_csv(ARTIFACTS / "threshold_sensitivity.csv", index=False)
    comparison_frame.to_csv(ARTIFACTS / "model_comparison.csv", index=False)
    importance_frame.to_csv(ARTIFACTS / "permutation_importance.csv", index=False)
    pd.DataFrame({
        "actual_below_threshold": y_test.to_numpy(),
        "predicted_below_threshold": predictions,
        "predicted_probability": probabilities,
    }).to_csv(ARTIFACTS / "test_predictions.csv", index=False)
    joblib.dump(selected_model, ARTIFACTS / "selected_model.joblib")

    result = {
        "dataset": "UCI Student Performance — Mathematics cohort (student-mat.csv)",
        "dataset_url": "https://archive.ics.uci.edu/dataset/320/student+performance",
        "dataset_audit": audit,
        "model_comparison": comparison_frame.to_dict(orient="records"),
        "test_metrics": metrics,
        "group_audit": group_audit,
        "methodology": {
            "target": "G3 < 10; an analytical threshold, not a diagnosis or student label",
            "predictors": "All available columns except G1, G2 and G3",
            "split": "75% train / 25% held-out test, stratified, random_state=42",
            "selection": "Highest mean 5-fold training CV F1; balanced accuracy used as tie-breaker",
            "preprocessing": "Median imputation + scaling for numeric; most-frequent imputation + one-hot encoding for categorical",
            "leakage_control": "All learned preprocessing is inside each model pipeline and fitted only within training folds",
            "importance": "Permutation importance on held-out test set after model selection; not used for tuning",
        },
        "limitations": [
            "The source data represents two Portuguese secondary schools, not Pakistan.",
            "The dataset is small and historically collected; performance may not generalize.",
            "The below-10 threshold is a research definition on this dataset's grade scale.",
            "Subgroup comparisons are descriptive and may be unstable at small sample sizes.",
            "Predictions must never be used for admissions, discipline, ranking, or denying support.",
        ],
    }
    with open(ARTIFACTS / "experiment_results.json", "w", encoding="utf-8") as file:
        json.dump(result, file, indent=2)
    return result
