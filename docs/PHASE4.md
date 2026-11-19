# Phase 4 — Calibration, uncertainty, robustness and error analysis

## Research objective
Assess whether predicted probabilities align with observed frequencies, quantify sampling uncertainty in held-out metrics, inspect classification errors, and describe variation across repeated training folds.

## Pre-specified design
- Target: G3 < 10 on the original 0–20 scale.
- Predictors: all available columns except G1, G2 and G3.
- Split: stratified 75/25, random_state=42.
- Model selection: training-only stratified five-fold CV, mean F1 with balanced accuracy as tie-breaker.
- Calibration: sigmoid calibration fitted using five-fold CV within the training partition. It is pre-specified and is not selected by held-out test performance.
- Decision threshold: 0.50, retained as a transparent analytical convention, not a recommended intervention threshold.
- Uncertainty: percentile bootstrap over held-out prediction/label pairs, with 95% intervals and valid-resample counts.
- Robustness: repeated stratified five-fold CV on the training partition for each baseline model family.

## Outputs
1. Raw versus calibrated Brier score, log loss, expected calibration error and reliability bins.
2. Reliability diagram data with observed positive rates and mean predicted probabilities.
3. Bootstrap confidence intervals for accuracy, balanced accuracy, precision, recall, F1, Brier score, log loss, expected calibration error and ROC-AUC when defined.
4. Confusion counts, false-positive and false-negative totals, overall error rate and descriptive group error summaries.
5. Repeated-CV means and standard deviations for F1 and balanced accuracy.
6. JSON export from the Streamlit workspace.

## Interpretation cautions
- A calibrated probability is not certainty about an individual learner.
- Bootstrap intervals on a small held-out sample can be wide and unstable; they do not establish external validity.
- Repeated CV on training data is a stability diagnostic, not a new independent test estimate.
- Group error-rate differences are descriptive and do not establish fairness or causation.
- The dataset represents two Portuguese secondary schools and is not validated for Pakistan.
- This prototype must never be used to rank, diagnose, punish, admit, exclude or deny support to learners.

## Run
```bash
streamlit run phase4.py
```
