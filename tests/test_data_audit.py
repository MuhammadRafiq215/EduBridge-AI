import unittest

import pandas as pd

from src.data import audit_dataset


class DatasetAuditTests(unittest.TestCase):
    def test_audit_reports_shape_duplicates_missing_and_target(self):
        frame = pd.DataFrame({
            "studytime": [2, 3, 3],
            "internet": ["yes", "no", "no"],
            "G3": [12, 8, 8],
        })
        result = audit_dataset(frame)
        self.assertEqual(result["rows"], 3)
        self.assertEqual(result["columns"], 3)
        self.assertEqual(result["duplicate_rows"], 1)
        self.assertEqual(result["missing_cells"], 0)
        self.assertEqual(result["below_threshold_count"], 2)
        self.assertEqual(result["at_or_above_threshold_count"], 1)
        self.assertEqual(result["excluded_grade_columns"], ["G1", "G2", "G3"])


class ThresholdSensitivityTests(unittest.TestCase):
    def test_threshold_tradeoffs_are_reported_without_selecting_a_winner(self):
        from src.modeling import threshold_sensitivity

        rows = threshold_sensitivity([0, 0, 1, 1], [0.1, 0.6, 0.4, 0.9], thresholds=(0.5,))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["threshold"], 0.5)
        self.assertAlmostEqual(rows[0]["precision"], 0.5)
        self.assertAlmostEqual(rows[0]["recall"], 0.5)
        self.assertIn("balanced_accuracy", rows[0])
        self.assertIn("predicted_positive_rate", rows[0])


if __name__ == "__main__":
    unittest.main()
