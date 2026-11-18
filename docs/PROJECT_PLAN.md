# EduBridge AI — Research Plan

## Research question
Can contextual and behavioural variables in a public educational dataset support a reproducible baseline classification experiment, and how should limitations be communicated?

## Phase 2 target
The experiment defines a binary target from UCI Mathematics final grade: G3 < 10 on the original 0–20 scale. This is an analytical threshold for this dataset, not a diagnosis or universal academic classification.

## Feature policy
G1, G2, and G3 are excluded from model predictors. UCI notes that G1 and G2 are strongly related to G3. Excluding prior grades makes the experiment more demanding and avoids presenting a grade-informed model as an early-support model.

## Experiment design
- Source: UCI Student Performance Mathematics cohort.
- Split: stratified 75/25 train/test, fixed random seed.
- Preprocessing: numeric median imputation and scaling; categorical most-frequent imputation and one-hot encoding.
- Leakage control: preprocessing is inside each estimator pipeline.
- Baselines: DummyClassifier, LogisticRegression, RandomForestClassifier.
- Validation: stratified 5-fold CV on training data.
- Selection: mean CV F1, with balanced accuracy as tie-breaker.
- Final test: held-out test metrics after model selection.
- Inspection: permutation importance on held-out data after evaluation.
- Group diagnostics: descriptive metrics for sex, school, and address where available.

## Metrics
Accuracy, balanced accuracy, precision, recall, F1, ROC-AUC, average precision, Brier score, confusion matrix, and classification report.

## Risks and safeguards
- **Dataset shift:** Portuguese schools are not a proxy for Pakistan. Do not claim local validity.
- **Target validity:** threshold is an experimental definition, not a policy or diagnosis.
- **Leakage:** do not use G1/G2 as predictors; keep learned preprocessing within CV pipelines.
- **Small sample:** report variability and avoid overclaiming subgroup findings.
- **Misuse:** never automate decisions about student opportunity or access to support.
- **Privacy:** no personal student data or secrets in Git.

## Next phases
1. Reproduce and inspect experiment outputs.
2. Add deeper EDA and sensitivity analysis.
3. Review group metrics, calibration, and error patterns.
4. Seek educator/researcher feedback before considering local data.
5. Only then consider a real-world pilot with appropriate governance and consent.
