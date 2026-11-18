"""Run the EduBridge AI Phase 2 experiment from the command line."""
from src.modeling import run_experiment

if __name__ == "__main__":
    results = run_experiment()
    print("Experiment completed.")
    print("Selected model:", results["test_metrics"]["selected_model"])
    print("Held-out F1:", round(results["test_metrics"]["f1"], 4))
    print("Held-out ROC-AUC:", round(results["test_metrics"]["roc_auc"], 4))
    print("Artifacts saved in artifacts/")
