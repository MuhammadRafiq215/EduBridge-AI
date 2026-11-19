# EduBridge AI
### A responsible educational analytics and machine-learning research prototype

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit"/>
  <img src="https://img.shields.io/badge/scikit--learn-ML-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white" alt="scikit-learn"/>
  <img src="https://img.shields.io/badge/Status-Research%20prototype-0F766E?style=for-the-badge" alt="Research prototype"/>
</p>

<p align="center"><strong>Every learner deserves a fair chance.</strong><br/>
A student-led project exploring how educational data can be audited, analysed and modelled transparently.</p>

---

## Table of contents

1. [Project vision](#project-vision)
2. [Development history](#development-history)
   - [Phase 1 — Initial application prototype](#phase-1--initial-application-prototype)
   - [Phase 2 — Reproducible machine-learning workflow](#phase-2--reproducible-machine-learning-workflow)
   - [Next phases](#next-phases)
3. [Current application features](#current-application-features)
4. [Dataset, target and feature policy](#dataset-target-and-feature-policy)
5. [Research methodology](#research-methodology)
6. [Repository structure](#repository-structure)
7. [Installation and local use](#installation-and-local-use)
8. [Streamlit deployment](#streamlit-deployment)
9. [Tests and quality checks](#tests-and-quality-checks)
10. [Responsible AI, privacy and limitations](#responsible-ai-privacy-and-limitations)
11. [References](#references)
12. [Author](#author)

## Project vision

EduBridge AI is a research and learning prototype. Its purpose is to demonstrate a transparent end-to-end data-science workflow: obtaining a public dataset, checking data quality, defining a research target, building leakage-aware machine-learning pipelines, evaluating models, and communicating limitations.

**It is not a student diagnosis, grading, admissions, ranking or intervention system.** It must not be used to make decisions about individual learners.

## Development history

The project is documented in chronological order so readers can understand how it evolved.

### Phase 1 — Initial application prototype

**Goal:** establish the first Streamlit application and the project's educational-analytics direction.

The initial prototype established:
- The EduBridge AI identity and Streamlit application entry point.
- A research-dashboard layout and navigation concept.
- The initial project structure and a foundation for later data-science work.
- The principle that the application should communicate educational data responsibly.

**Phase 1 outcome:** a working interface concept and a foundation for the research workflow. It did not yet constitute a complete, validated machine-learning experiment.

### Phase 2 — Reproducible machine-learning workflow

**Goal:** turn the initial interface into a documented, reproducible baseline ML research application.

Implemented capabilities:
- Download the official UCI Student Performance archive at experiment time.
- Load the Mathematics cohort and audit dimensions, duplicates and missing values.
- Define an explicit binary research target from final grade G3.
- Exclude G1, G2 and G3 from model predictors.
- Apply numeric and categorical preprocessing inside scikit-learn pipelines.
- Compare a Dummy baseline, Logistic Regression and Random Forest.
- Use stratified five-fold cross-validation on training data.
- Select a model using mean cross-validation F1, with balanced accuracy as a tie-breaker.
- Evaluate the selected pipeline on one held-out test partition.
- Report classification, ranking and probability metrics.
- Inspect feature permutation importance after model selection.
- Produce descriptive subgroup diagnostics with clear cautions.
- Save experiment outputs locally and offer dashboard downloads.
- Run automated compilation and unit-test checks with GitHub Actions.

**Phase 2 outcome:** the code for an end-to-end baseline research workflow is implemented. Actual experiment results are generated only when the experiment is run; no performance scores are fabricated or pre-filled.

### Phase 3 — Deeper exploratory analysis and target-definition sensitivity

**Goal:** examine descriptive patterns and test whether baseline conclusions depend on the definition of the positive class.

Implemented in `src/exploration.py` with a separate Streamlit workspace in `phase3.py`:
- Descriptive final-grade distribution, numeric summaries, feature/grade correlations and categorical distributions.
- Sensitivity scenarios `G3 < 8`, `G3 < 10`, and `G3 < 12` on the original 0–20 scale.
- Separate model selection for each target using the same stratified 75/25 split seed and five-fold training CV.
- G1, G2 and G3 remain excluded from predictors in every scenario.
- Reports class prevalence, selected model, CV metrics and held-out metrics without declaring a preferred cut-off.
- Unit tests and a detailed methodology note in `docs/PHASE3.md`.

Run with `streamlit run phase3.py`. These cut-offs are analytical scenarios, not diagnoses or school-policy recommendations.

### Next phases

- [ ] Run Phase 3 in the hosted environment and review generated outputs.
- [ ] Examine calibration and error patterns.
- [ ] Seek independent educator/researcher review.
- [ ] Investigate an appropriate local dataset only with consent, governance and privacy safeguards.
- [ ] Do not present the prototype as deployment-ready for real student decisions.

## Current application features

The Streamlit dashboard contains seven workspaces:

| Workspace | Purpose |
|---|---|
| Research Overview | Dataset and experiment summary, model comparison and headline metrics |
| Dataset Explorer | Dataset audit, preview, grade distribution and missingness |
| Model Lab | Cross-validation comparison of baseline estimators |
| Evaluation | Held-out metrics, confusion matrix, ROC curve, classification report and threshold-sensitivity diagnostics |
| Explainability | Permutation-importance inspection |
| Responsible AI | Descriptive subgroup diagnostics and safeguards |
| Methodology | Experiment settings, limitations and downloadable artifacts |

The first launch intentionally displays instructions until the user runs the experiment from the sidebar.

## Dataset, target and feature policy

**Dataset:** [UCI Machine Learning Repository — Student Performance](https://archive.ics.uci.edu/dataset/320/student+performance), Mathematics file (`student-mat.csv`).

The source dataset describes students from two Portuguese secondary schools. It is not a representative sample of Pakistani learners.

**Positive class:** `G3 < 10` on the dataset's original 0–20 final-grade scale. This is an analytical threshold for this experiment only. It is not a diagnosis, universal definition of academic difficulty or recommended school policy.

### Feature leakage policy

The model excludes:
- `G3`, because it defines the target.
- `G1` and `G2`, because they are earlier grades strongly related to G3.

This is intended to make the experiment a more demanding contextual-feature study. It does not prove that the remaining features are appropriate for real-world educational decisions.

## Research methodology

| Stage | Design |
|---|---|
| Data split | Stratified 75% training / 25% held-out test |
| Random seed | 42 |
| Numeric features | Median imputation, then standard scaling |
| Categorical features | Most-frequent imputation, then one-hot encoding |
| Leakage control | Preprocessing is part of each estimator pipeline and fitted within CV folds |
| Baselines | Dummy prior, Logistic Regression, Random Forest |
| Validation | Stratified 5-fold CV on training data |
| Selection | Highest mean CV F1; balanced accuracy tie-breaker |
| Final evaluation | One held-out test partition after model selection |
| Interpretation | Permutation importance on held-out data after selection; not used for tuning |
| Group diagnostics | Descriptive metrics for sex, school and address where available |

Reported metrics include accuracy, balanced accuracy, precision, recall, F1, ROC-AUC, average precision, Brier score, confusion matrix and classification report. No single metric establishes that a model is safe or suitable for real-world use.

The pipeline design follows the scikit-learn guidance on [common pitfalls and data leakage](https://scikit-learn.org/stable/common_pitfalls/) and [composite estimators](https://scikit-learn.org/stable/modules/compose.html).

## Repository structure

```text
EduBridge-AI/
├── .github/
│   └── workflows/
│       └── ci.yml
├── .streamlit/
│   └── config.toml
├── docs/
│   ├── DEPLOYMENT.md
│   └── PROJECT_PLAN.md
├── src/
│   ├── __init__.py
│   ├── data.py
│   └── modeling.py
├── tests/
│   └── test_data_audit.py
├── .gitignore
├── app.py
├── requirements.txt
├── train.py
└── README.md
```

Generated files are stored under `artifacts/` at runtime and excluded from Git:
- `experiment_results.json`
- `model_comparison.csv`
- `permutation_importance.csv`
- `test_predictions.csv`
- `selected_model.joblib`

## Installation and local use

### Requirements

- Python 3.12 recommended.
- Internet connection for the first dataset download.
- Git (optional, for cloning the repository).

### 1. Clone the repository

```bash
git clone https://github.com/MuhammadRafiq215/EduBridge-AI.git
cd EduBridge-AI
```

### 2. Create and activate a virtual environment

**Windows PowerShell**
```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux**
```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Start the dashboard

```bash
streamlit run app.py
```

Open the local address printed in the terminal. In the app sidebar, select **Run / refresh experiment** to download the dataset, train and evaluate the baselines, and generate the artifacts.

To run the experiment without opening the dashboard:

```bash
python train.py
```

## Streamlit deployment

See the full [Streamlit deployment guide](docs/DEPLOYMENT.md).

The Streamlit Community Cloud app must be created by an account holder who can authorize access to this GitHub repository. Required settings:
- Repository: `MuhammadRafiq215/EduBridge-AI`
- Branch: `main`
- Main file: `app.py`
- Python: `3.12`

The final public app URL is assigned/confirmed by Streamlit during deployment. A repository URL is not a live application URL, and search engines may take time to index a newly published site. Never treat a guessed URL as a deployed address.

## Tests and quality checks

Run the local test suite:

```bash
python -m compileall -q app.py train.py src tests
python -m unittest discover -s tests -v
```

GitHub Actions runs the same compilation and unit-test checks on pushes and pull requests to `main`. A green workflow confirms those checks passed; it does not by itself prove that the full live Streamlit application or UCI download has been exercised.

## Responsible AI, privacy and limitations

1. The dataset comes from two Portuguese schools and is not validated for Pakistan.
2. The sample is limited and historical; performance may not generalize to another school, country, time period or population.
3. The G3 threshold is an experiment-specific label, not a diagnosis or policy recommendation.
4. Subgroup metrics are descriptive only. Small groups can produce unstable estimates and do not establish fairness.
5. Permutation importance describes model behaviour, not causation.
6. Never use this prototype to rank, punish, diagnose, admit, exclude or determine access to support for a learner.
7. Any future real-world study requires local data governance, appropriate consent, privacy protection, expert review and independent evaluation.
8. Never commit passwords, API keys, identifiable student records or other private information.

## References

- Cortez, P. & Silva, A. (2008). *Using Data Mining to Predict Student Performance*. FUBUTEC 2008.
- [UCI Student Performance dataset](https://archive.ics.uci.edu/dataset/320/student+performance)
- [scikit-learn — Common pitfalls and data leakage](https://scikit-learn.org/stable/common_pitfalls/)
- [scikit-learn — Pipelines and ColumnTransformer](https://scikit-learn.org/stable/modules/compose.html)
- [scikit-learn — Cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html)
- [scikit-learn — Permutation importance](https://scikit-learn.org/stable/modules/permutation_importance.html)
- [Streamlit Community Cloud deployment](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app)

## Author

**Muhammad Rafique** · AI & Data Science student

- GitHub: [@MuhammadRafiq215](https://github.com/MuhammadRafiq215)
- Project repository: [EduBridge AI](https://github.com/MuhammadRafiq215/EduBridge-AI)
- Email: [muhammadrafiqcoder@gmail.com](mailto:muhammadrafiqcoder@gmail.com)

<p align="center"><strong>Learn · Analyze · Build · Improve</strong></p>
