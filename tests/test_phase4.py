import unittest

import numpy as np
import pandas as pd

from src.phase4 import (
    bootstrap_confidence_intervals, calibration_bins,
    expected_calibration_error, run_phase4_analysis,
)


class Phase4MetricTests(unittest.TestCase):
    def test_calibration_bins_cover_probabilities_and_counts(self):
        y = [0, 0, 1, 1]
        p = [0.1, 0.4, 0.6, 0.9]
        bins = calibration_bins(y, p, n_bins=2)
        self.assertEqual(sum(row["count"] for row in bins), 4)
        self.assertEqual(len(bins), 2)
        self.assertGreaterEqual(expected_calibration_error(y, p, n_bins=2), 0)

    def test_bootstrap_intervals_are_reproducible_and_bounded(self):
        y = [0, 0, 1, 1, 0, 1, 0, 1]
        p = [0.1, 0.2, 0.8, 0.7, 0.4, 0.6, 0.3, 0.9]
        first = bootstrap_confidence_intervals(y, p, repeats=200, random_state=7)
        second = bootstrap_confidence_intervals(y, p, repeats=200, random_state=7)
        self.assertEqual(first, second)
        self.assertLessEqual(first["intervals"]["f1"]["lower"], first["intervals"]["f1"]["upper"])
        self.assertGreaterEqual(first["intervals"]["brier_score"]["lower"], 0)
        self.assertLessEqual(first["intervals"]["brier_score"]["upper"], 1)

    def test_phase4_rejects_too_few_training_examples_for_five_fold_cv(self):
        # Five observations per class in the full frame become fewer than five
        # per class after the stratified training split.
        frame = pd.DataFrame({
            "studytime": list(range(10)),
            "school": ["A", "B"] * 5,
            "G1": [7, 8, 11, 12, 6, 9, 13, 14, 5, 15],
            "G2": [8, 9, 12, 13, 7, 10, 14, 15, 6, 16],
            "G3": [6, 7, 11, 12, 8, 9, 13, 14, 5, 15],
        })
        with self.assertRaisesRegex(ValueError, "at least five observations"):
            run_phase4_analysis(frame, bootstrap_repeats=200, robustness_repeats=2)

    def test_phase4_pipeline_excludes_grade_columns(self):
        frame = pd.DataFrame({
            "studytime": [1, 2, 3, 4] * 30,
            "failures": [0, 1, 0, 2] * 30,
            "school": ["A", "B"] * 60,
            "sex": ["F", "M", "M", "F"] * 30,
            "G1": [8, 9, 10, 11] * 30,
            "G2": [9, 10, 11, 12] * 30,
            "G3": [6, 8, 9, 12, 13, 14, 15, 16] * 15,
        })
        result = run_phase4_analysis(
            frame, bootstrap_repeats=200, robustness_repeats=2
        )
        self.assertEqual(result["sample_sizes"]["total"], 120)
        self.assertEqual(result["probability_calibration"]["method"].startswith("Sigmoid"), True)
        self.assertEqual(result["uncertainty"]["calibrated_model"]["confidence_level"], 0.95)
        self.assertIn("sex", result["error_analysis"]["group_diagnostics"])
        self.assertNotIn("G1", result["methodology"]["predictor_columns"])
        self.assertNotIn("G2", result["methodology"]["predictor_columns"])
        self.assertNotIn("G3", result["methodology"]["predictor_columns"])
        self.assertEqual(result["robustness"]["results"][0]["folds"], 10)


if __name__ == "__main__":
    unittest.main()
