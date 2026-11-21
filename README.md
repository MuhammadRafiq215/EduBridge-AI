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
2. [Student-facing experience](#student-facing-experience)
3. [Machine-learning research](#machine-learning-research)
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

## Student-facing experience

The main Streamlit app is designed around the learner rather than development milestones. Its workspaces are:

| Workspace | What a learner can do |
|---|---|
| Dashboard | Review your saved learning snapshot, subject confidence and next priorities |
| My learning profile | Select an education level from middle school through BS, record subjects, choose a field and self-rate confidence |
| Career pathways | Explore preparation areas, degree families and small project ideas across engineering, computing/AI, medicine/health, economics/business, sciences, social sciences and design |
| Study planner | Turn self-reported priorities and available weekly time into a simple study allocation |
| Research insights | Inspect public-dataset experiments and compare machine-learning model families |
| Student feedback | Submit anonymous usability feedback without creating an account |
| Account & privacy | Create an account, sign in, reset a password and manage saved profile data |
| About EduBridge | Review the platform's scope, privacy and limitations |

Student accounts use Supabase Auth for email/password registration and sign-in. Learner profiles are stored in PostgreSQL and protected by row-level security. Run supabase/schema.sql and add the project URL and publishable/anon key to Streamlit secrets before enabling account features. The app never needs the service-role key.

The confidence snapshot is based only on the learner's own ratings. It is not an objective grade, admissions probability, diagnosis or AI prediction.

### AI Teacher, Student Navigator and adaptive progress

EduBridge includes a specification-aware AI Teacher, a Student Navigator, opt-in topic-progress tracking, guided practice and a transparent revision queue. The Guided Practice Studio can generate subject-aware practice and formative feedback when an authorised provider is configured; without a model, it clearly switches to a general recall/explain/apply scaffold and never pretends to generate or mark subject answers. Topic reflections are self-reported and are not formal grades. Revision dates use transparent rule-based intervals. The AI Teacher supports a local model runtime for same-computer use and an explicitly configured hosted OpenAI-compatible provider. A live response requires a running/configured model; the interface never fabricates connectivity. See [AI Teacher runtime setup](docs/AI_TEACHER_RUNTIME.md), [Phase 14](docs/PHASE14_GENERATIVE_AI_TEACHER.md) and [Phase 15](docs/PHASE15_ADAPTIVE_LEARNING_EXPERIENCE.md).

## Machine-learning research

The current secondary-school benchmark uses the [UCI Student Performance dataset](https://archive.ics.uci.edu/dataset/320/student+performance). Its mathematics cohort represents two Portuguese schools, so it is a methodological benchmark—not a validated model for Pakistani students.

The benchmark compares:
- Dummy baseline
- Logistic Regression
- Random Forest
- Extra Trees
- Gradient Boosting
- RBF Support Vector Machine
- K-Nearest Neighbours

All preprocessing remains inside scikit-learn pipelines. Model selection uses stratified cross-validation on training data, followed by one held-out evaluation. The user-facing learner profile is not passed into these research models.

### Additional datasets under evaluation

These sources have different populations, features and outcomes. They must be modelled and evaluated separately rather than concatenated into one misleading training table.

- [Open University Learning Analytics Dataset (OULAD)](https://archive.ics.uci.edu/dataset/349/open+university+learning+analytics+dataset): more than 30,000 higher-education registrations with course and online-learning activity; suitable for a separate higher-education learning-analytics experiment.
- [Higher Education Students Performance Evaluation](https://archive.ics.uci.edu/dataset/856/higher+education+students+performance+evaluation): 145 records from engineering and educational-science faculties; a small exploratory benchmark, not a basis for broad claims.
- [Engineering student performance dataset](https://data.mendeley.com/datasets/83tcx8psxv/1): a separate engineering-focused dataset of 12,411 students; review schema, licence and target definitions before integration.

No benchmark listed above represents every medical, economics, engineering or BS programme. Career pathway content is orientation guidance, not a claim that the ML models have been trained for those disciplines.

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
├── .github/workflows/ci.yml
├── .streamlit/config.toml
├── docs/
│   ├── DEPLOYMENT.md
│   ├── PHASE3.md
│   ├── PHASE4.md
│   ├── PHASE5.md
│   ├── PROJECT_PLAN.md
│   └── STUDENT_PILOT.md
├── supabase/
│   ├── schema.sql
│   └── feedback_schema.sql
├── src/
│   ├── __init__.py
│   ├── account_store.py
│   ├── feedback.py
│   ├── profile_export.py
│   ├── research_ui.py
│   ├── student_guidance.py
│   ├── data.py
│   ├── exploration.py
│   ├── explainability.py
│   ├── modeling.py
│   └── phase4.py
├── tests/
│   ├── test_data_audit.py
│   ├── test_explainability.py
│   ├── test_phase3.py
│   └── test_phase4.py
├── .gitignore
├── app.py
├── phase3.py
├── phase4.py
├── phase5.py
├── requirements.txt
└── train.py
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

Open the local address printed in the terminal. Configure Supabase secrets before testing account creation and persistent profile storage. Use **Research insights** to run the public-dataset benchmark.

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

## Student pilot

Use [docs/STUDENT_PILOT.md](docs/STUDENT_PILOT.md) for a structured usability pilot. The Student feedback workspace stores a rating, selected workspace, category and short comment without asking for a name or contact details. To enable it, run the separate `supabase/feedback_schema.sql` file once in the Supabase SQL Editor. The feedback table is insert-only for visitors; review submissions in the Supabase SQL Editor.

## Tests and quality checks

Run the local test suite:

```bash
python -m compileall -q app.py phase3.py phase4.py phase5.py train.py src tests
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
9. Use only the Supabase publishable/anon key in Streamlit secrets; never expose the service-role key.
10. Keep row-level security enabled on student_profiles so each learner can access only their own row.
11. The optional student_feedback table accepts inserts only from visitors; it does not grant visitors permission to read other submissions.

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
