# EduBridge AI — Project Plan

## Research question
How might responsible educational analytics help educators understand learning patterns and consider appropriate, human-led academic support?

## Current stage
Phase 1: Streamlit interface prototype using synthetic demonstration records. There is no trained model and no live prediction functionality.

## Planned phases
1. **Data audit:** select a documented dataset; review licence, schema, missingness, target options, class balance, and limitations.
2. **Exploratory analysis:** describe distributions and relationships without causal claims.
3. **Baseline modelling:** define a defensible target and compare simple models with leakage-safe validation.
4. **Evaluation:** report suitable metrics, error patterns, calibration where relevant, and subgroup checks where data quality permits.
5. **Explainability:** use suitable feature-importance or SHAP methods while explaining their limitations.
6. **Application integration:** connect only a validated model and retain human oversight.

## Initial dataset candidate
The UCI Student Performance dataset is a candidate for initial exploration. It represents Portuguese schools, so findings must not be assumed to transfer to Pakistan or other education systems.

## Success criteria
- Reproducible data preparation and experiments
- Clearly documented target and feature choices
- Baseline comparisons and transparent evaluation
- Honest discussion of uncertainty, bias, and generalization
- No automated decisions about students

## Risks and safeguards
- **Target leakage:** define the target before feature selection and inspect feature timing.
- **Dataset shift:** document the original population and avoid unsupported generalization.
- **Privacy:** do not publish personal student records or credentials.
- **Misuse:** position outputs as decision-support prompts, never final judgments.
