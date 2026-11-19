# Phase 5 — Explainable AI with SHAP

## Goal
Add model-agnostic global and record-level explanations to help researchers inspect how a baseline model uses contextual features.

## Method
- Define the research label as G3 < 10 on the source 0–20 scale.
- Exclude G1, G2 and G3 from predictors.
- Use the existing stratified 75/25 split with random_state=42.
- Select the baseline model using stratified five-fold cross-validation on the training partition only.
- Fit the selected pipeline on the training partition.
- Sample the SHAP background only from training rows.
- Explain a small deterministic sample of held-out rows using SHAP PermutationExplainer.
- Report mean absolute SHAP contributions globally and signed contributions for a selected sample record.

## Run
```bash
pip install -r requirements.txt
streamlit run phase5.py
```

## Interpretation and safeguards
SHAP values describe the fitted model's attribution relative to a selected background. They do not show that a feature causes an outcome, that changing a feature will change a learner's result, or that the model is fair. Correlated predictors can share or redistribute attribution. The sample is from two Portuguese schools and is not validated for Pakistan. Do not use the prototype to rank, diagnose, punish, admit, exclude or deny support to learners.

## Computational scope
The dashboard defaults to 40 training background rows and 25 held-out explanation rows. Both can be adjusted. Permutation SHAP can be computationally expensive; use modest samples for the hosted demo.
