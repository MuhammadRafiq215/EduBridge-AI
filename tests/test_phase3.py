import unittest

import pandas as pd

from src.exploration import exploratory_summary, target_sensitivity


class Phase3ExplorationTests(unittest.TestCase):
    def setUp(self):
        self.frame = pd.DataFrame({
            "studytime": [1, 2, 3, 4] * 20,
            "failures": [0, 1, 0, 2] * 20,
            "school": ["A", "B"] * 40,
            "G1": [8, 9, 10, 11] * 20,
            "G2": [9, 10, 11, 12] * 20,
            "G3": [6, 8, 9, 12, 13, 14, 15, 16] * 10,
        })

    def test_exploratory_summary_reports_grade_counts_and_correlations(self):
        result = exploratory_summary(self.frame)
        self.assertEqual(result["rows"], 80)
        self.assertEqual(sum(row["count"] for row in result["grade_counts"]), 80)
        self.assertTrue(result["grade_correlations"])

    def test_target_sensitivity_excludes_grade_predictors(self):
        rows = target_sensitivity(self.frame, thresholds=(8, 10, 12))
        self.assertEqual(len(rows), 3)
        self.assertTrue(all(row["status"] in {
            "evaluated", "insufficient_class_support"
        } for row in rows))
        self.assertTrue(all("G1" not in row and "G2" not in row for row in rows))


if __name__ == "__main__":
    unittest.main()
