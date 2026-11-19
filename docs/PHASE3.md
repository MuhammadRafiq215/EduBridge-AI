# Phase 3 — Deeper exploratory analysis and target-definition sensitivity

## Purpose
Phase 3 examines how descriptive patterns and baseline model results depend on the operational definition of the positive class. It is a research sensitivity exercise, not a search for the “best” label for students.

## Target scenarios
On the UCI Mathematics cohort's original 0–20 final-grade scale, the analysis evaluates:
- G3 < 8
- G3 < 10 (the Phase 2 reference definition)
- G3 < 12

These cut-offs are analytical scenarios only. They are not diagnoses, universal academic standards, or recommendations for school policy.

## Analysis
1. Describe the final-grade distribution.
2. Summarize numeric variables and their descriptive association with G3.
3. Summarize categorical feature distributions.
4. Re-run the baseline model comparison separately for each target definition.
5. Use the same 75/25 stratified split seed (42), five-fold stratified CV on training data, and model family.
6. Exclude G1, G2 and G3 from predictors in every scenario.
7. Report class prevalence, selected model, cross-validation F1 and balanced accuracy, and held-out precision, recall, F1 and balanced accuracy.

## Interpretation safeguards
- A change in target definition changes the classification task. Scores across definitions are not a direct leaderboard.
- Each definition can select a different model; this is reported rather than hidden.
- No cut-off is selected as a recommended student label or intervention policy.
- Correlation is not causation; subgroup patterns do not establish fairness.
- The UCI sample represents two Portuguese schools and does not validate the approach for Pakistan.
- Never use outputs to rank, diagnose, punish, admit, exclude, or deny support to learners.

## Run
Install requirements, then launch the separate Phase 3 workspace:

```bash
streamlit run phase3.py
```

The dashboard downloads the official UCI Mathematics dataset when the user starts the analysis and offers a JSON export. Generated outputs are local runtime artifacts and should not be committed.
