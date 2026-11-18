# 🎓 EduBridge AI
### Responsible Educational Analytics · Phase 2: Baseline Machine Learning

<p align="center">
<img src="https://img.shields.io/badge/Phase-02%20ML%20Research-0f766e?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white"/>
<img src="https://img.shields.io/badge/scikit--learn-Modeling-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white"/>
</p>
<p align="center"><b>Every learner deserves a fair chance.</b><br/>A student-led research prototype for reproducible data exploration, leakage-aware machine learning, transparent evaluation, and responsible interpretation.</p>

---

## 🔬 Phase 2 overview

Phase 2 develops the initial interface into a reproducible baseline ML workflow using the **UCI Student Performance Mathematics cohort**.

- Official dataset download when the experiment runs
- Dataset quality audit and exploratory views
- Explicit target definition and grade-feature leakage prevention
- Numeric and categorical preprocessing inside scikit-learn pipelines
- Dummy, Logistic Regression, and Random Forest baselines
- Stratified 5-fold cross-validation on training data
- Model selection using cross-validation F1
- One held-out test evaluation with multiple metrics
- Confusion matrix, ROC curve, classification report, and probability metrics
- Post-evaluation permutation importance
- Descriptive subgroup diagnostics and responsible-use guidance
- Downloadable experiment artifacts

**No performance scores are invented or hard-coded.** Run the experiment to generate metrics from the dataset.

## 📊 Dataset and target

Source: [UCI Machine Learning Repository — Student Performance](https://archive.ics.uci.edu/dataset/320/student+performance).

This project uses the **Mathematics file** (`student-mat.csv`). UCI describes the data as coming from two Portuguese secondary schools and notes that final grade G3 is strongly related to earlier grades G1 and G2. This dataset is not representative evidence about Pakistani learners.

Positive class: `G3 < 10` on the original 0–20 scale. This is an analytical threshold for this experiment—not a diagnosis or universal definition of academic difficulty.

### Leakage-aware feature policy

The model excludes **G1, G2, and G3** from predictors. G3 defines the target; G1 and G2 are earlier grades strongly associated with G3. This creates a more demanding early-support research question using the remaining contextual and behavioural features.

## 🧪 Experimental design

| Stage | Implementation |
|---|---|
| Audit | Dimensions, duplicates, missingness, target distribution |
| Split | Stratified 75% train / 25% held-out test |
| Numeric preprocessing | Median imputation + standard scaling |
| Categorical preprocessing | Most-frequent imputation + one-hot encoding |
| Leakage control | Learned transformations live inside model pipelines |
| Baselines | Dummy prior, Logistic Regression, Random Forest |
| Validation | Stratified 5-fold CV on training partition |
| Selection | Highest mean CV F1; balanced accuracy tie-breaker |
| Final test | Held-out metrics after model selection |
| Interpretation | Permutation importance after evaluation |

The scikit-learn pipeline approach helps prevent preprocessing leakage across validation folds. See the [common pitfalls guide](https://scikit-learn.org/stable/common_pitfalls/) and [Pipeline / ColumnTransformer documentation](https://scikit-learn.org/stable/modules/compose.html).

### Evaluation metrics

Accuracy, balanced accuracy, precision, recall, F1, ROC-AUC, average precision, Brier score, confusion matrix, and classification report. No single metric proves that a model is suitable for real-world use.

## 🖥️ Run locally

```bash
git clone https://github.com/MuhammadRafiq215/EduBridge-AI.git
cd EduBridge-AI
python -m venv .venv
```

Activate the environment:

**Windows PowerShell**
```powershell
.venv\Scripts\Activate.ps1
```

**macOS / Linux**
```bash
source .venv/bin/activate
```

Install and launch:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
streamlit run app.py
```

Open the local URL shown by Streamlit. Select **Run / refresh experiment** in the sidebar. Alternatively run:

```bash
python train.py
```

The app downloads the UCI archive, runs cross-validation, evaluates the selected baseline on the held-out test set, and saves results locally.

## 🗂️ Project structure

```text
EduBridge-AI/
├── app.py
├── train.py
├── requirements.txt
├── README.md
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── data.py
│   └── modeling.py
├── docs/
│   └── PROJECT_PLAN.md
└── artifacts/  # generated locally; excluded from Git
```

### Generated artifacts

- `experiment_results.json` — audit, methodology, CV results, test metrics, subgroup diagnostics
- `model_comparison.csv` — cross-validation means and standard deviations
- `permutation_importance.csv` — feature importance estimates
- `test_predictions.csv` — held-out labels, predictions, probabilities
- `selected_model.joblib` — locally saved fitted pipeline

Generated artifacts and model binaries are ignored by Git to keep the repository lightweight and avoid publishing unreviewed outputs.

## 🛡️ Responsible AI and limitations

1. The source data represents two Portuguese schools; it is not representative evidence about Pakistan.
2. Random-split performance does not establish generalization to another country, school, time period, or population.
3. Subgroup metrics are descriptive diagnostics, not proof of fairness; small groups can make estimates unstable.
4. Feature importance describes model behaviour, not causation.
5. Predictions must never be used to rank, punish, diagnose, admit, or exclude students.
6. A real-world pilot would require local data governance, consent, expert review, and independent evaluation.
7. Never commit identifiable student data, credentials, or private records.

## 🗺️ Roadmap

- [x] Phase 1 — initial Streamlit interface
- [x] Phase 2 — data audit and baseline ML workflow implementation
- [x] Leakage-aware preprocessing and held-out evaluation implementation
- [ ] Execute and review experiment outputs in the deployment environment
- [ ] Add a reproducible EDA report and research notebook
- [ ] Sensitivity analysis and stronger validation design
- [ ] Independent review of subgroup and error analysis
- [ ] Local-context research before Pakistan-specific claims
- [ ] Phase 3 — validated model integration and deployment

## 📚 References

- Cortez, P. & Silva, A. (2008). *Using Data Mining to Predict Student Performance*. FUBUTEC 2008.
- [UCI Student Performance dataset](https://archive.ics.uci.edu/dataset/320/student+performance)
- [scikit-learn: Common pitfalls and data leakage](https://scikit-learn.org/stable/common_pitfalls/)
- [scikit-learn: Pipelines and ColumnTransformer](https://scikit-learn.org/stable/modules/compose.html)
- [scikit-learn: Cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html)
- [scikit-learn: Permutation importance](https://scikit-learn.org/stable/modules/permutation_importance.html)

## 👨‍💻 Author

**Muhammad Rafique** · AI & Data Science student

- GitHub: [@MuhammadRafiq215](https://github.com/MuhammadRafiq215)
- Project: [EduBridge AI](https://github.com/MuhammadRafiq215/EduBridge-AI)
- Email: [muhammadrafiqcoder@gmail.com](mailto:muhammadrafiqcoder@gmail.com)

<p align="center"><b>Learn · Analyze · Build · Improve</b></p>
