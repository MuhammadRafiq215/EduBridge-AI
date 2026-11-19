# EduBridge AI — Project and Research Plan

## 1. Project purpose

EduBridge AI is a student-led research prototype for responsible educational data exploration and baseline machine-learning experimentation. It is not a diagnostic, grading, admissions, ranking or intervention system.

## 2. Development phases

### Phase 1 — Initial application prototype

**Objective:** establish the first Streamlit interface and the educational-analytics project foundation.

Initial deliverables:
- Project identity and Streamlit entry point.
- Dashboard layout and navigation concept.
- Initial project structure.
- Responsible-use direction for educational analytics.

**Outcome:** an interface prototype and a foundation for the later research workflow. Phase 1 did not claim to be a validated predictive system.

### Phase 2 — Reproducible baseline ML research

**Objective:** implement an end-to-end experiment using a public dataset with transparent evaluation.

Deliverables:
- Download and load the UCI Mathematics cohort.
- Audit dataset dimensions, duplicates and missingness.
- Define G3 < 10 as the experiment-specific positive class.
- Exclude G1, G2 and G3 from predictors.
- Use numeric and categorical preprocessing inside scikit-learn pipelines.
- Compare Dummy, Logistic Regression and Random Forest baselines.
- Use stratified five-fold CV on the training partition.
- Select using mean CV F1, with balanced accuracy as a tie-breaker.
- Evaluate once on the held-out test partition.
- Report classification and probability metrics.
- Calculate permutation importance after model selection.
- Produce descriptive subgroup diagnostics.
- Save reproducible artifacts locally and document limitations.

### Future Phase 3 — Validation before any real-world pilot

Phase 3 is a proposal, not a completed feature set. It should begin only after Phase 2 experiment outputs have been generated and reviewed.

Potential work:
- Sensitivity analysis for the G3 threshold.
- Deeper exploratory data analysis.
- Calibration and error analysis.
- Independent educator/researcher review.
- A separate validation design for any local-context research.
- Privacy, consent, governance and data-security review before collecting or using any local data.

## 3. Dataset and target

Source: [UCI Student Performance](https://archive.ics.uci.edu/dataset/320/student+performance), Mathematics cohort (`student-mat.csv`).

The dataset represents two Portuguese secondary schools. It is not a representative sample of Pakistani learners.

The positive class is defined as G3 < 10 on the original 0–20 scale. This is an analytical threshold for this experiment only, not a diagnosis or universal definition of academic difficulty.

## 4. Feature policy and leakage control

G3 defines the target and is therefore excluded from predictors. G1 and G2 are also excluded because they are earlier grades strongly related to G3. All learned preprocessing is placed inside each estimator pipeline so it is fitted within the cross-validation training folds.

## 5. Experimental design

- Stratified 75/25 train/test split with fixed random seed 42.
- Numeric preprocessing: median imputation and standard scaling.
- Categorical preprocessing: most-frequent imputation and one-hot encoding.
- Baselines: DummyClassifier, LogisticRegression and RandomForestClassifier.
- Validation: stratified five-fold cross-validation on training data.
- Selection: highest mean CV F1, balanced accuracy as tie-breaker.
- Final evaluation: held-out test partition after model selection.
- Model inspection: permutation importance on held-out data after evaluation.
- Group diagnostics: descriptive summaries for sex, school and address where available.

## 6. Metrics

Accuracy, balanced accuracy, precision, recall, F1, ROC-AUC, average precision, Brier score, confusion matrix and classification report.

## 7. Risks and safeguards

- **Dataset shift:** Portuguese school data is not a proxy for Pakistan. Do not claim local validity.
- **Target validity:** the threshold is an experiment definition, not a diagnosis or school policy.
- **Leakage:** do not use G1/G2 as predictors; keep learned preprocessing inside CV pipelines.
- **Small sample:** report variability and avoid overclaiming subgroup findings.
- **Misuse:** never automate decisions about student opportunity or access to support.
- **Privacy:** do not commit identifiable student data, credentials or secrets.

## 8. Completion criteria for the next milestone

- GitHub Actions compilation and unit tests pass.
- The hosted app starts successfully.
- The UCI dataset download and full experiment complete in the hosted runtime.
- Generated metrics and artifacts are reviewed for plausibility.
- Limitations and non-decision-use safeguards remain visible in the app and documentation.


## 9. Phase 3 implementation

Phase 3 is implemented in `src/exploration.py` and exposed through the standalone Streamlit workspace `phase3.py`. It reports descriptive grade distributions, numeric summaries, numeric-feature correlations with G3, categorical distributions, and target sensitivity for G3 < 8, G3 < 10, and G3 < 12. Each target definition is evaluated as a separate classification task using the same stratified 75/25 split seed (42), five-fold CV on training data, and the existing model family. G1, G2 and G3 remain excluded from predictors. See `docs/PHASE3.md` for assumptions, interpretation safeguards and run instructions. The scenarios are not recommendations for academic labels or interventions.


## 10. Phase 4 implementation

Phase 4 is implemented in `src/phase4.py` and exposed through `phase4.py`. It adds pre-specified sigmoid calibration trained only within the training partition, raw-versus-calibrated reliability analysis, Brier score, log loss, expected calibration error, percentile-bootstrap confidence intervals on held-out predictions, false-positive/false-negative analysis, descriptive subgroup error summaries, and repeated stratified five-fold training-CV stability diagnostics. The held-out test set is not used for model or calibration selection. See `docs/PHASE4.md`. Run with `streamlit run phase4.py`.


### Phase 5 — Explainable AI with SHAP

Implemented in `src/explainability.py` with a dedicated Streamlit workspace in `phase5.py`:
- Model-agnostic SHAP permutation explanations for a small held-out sample.
- Global mean-absolute contribution summaries and signed record-level contributions.
- Model selection and fitting restricted to the training partition; SHAP background sampled from training rows.
- Leakage exclusions for G1, G2 and G3 remain enforced.
- Interpretation notes distinguish model attribution from causation and educational decisions.

Run with `streamlit run phase5.py`. See `docs/PHASE5.md` for methodology and safeguards.
