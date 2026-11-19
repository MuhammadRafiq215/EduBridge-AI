import unittest

import numpy as np

from src.explainability import summarize_shap_values


class ExplainabilitySummaryTests(unittest.TestCase):
    def test_global_summary_orders_mean_absolute_contribution(self):
        values = np.array([[0.1, -0.8], [-0.2, 0.4], [0.3, -0.6]])
        result = summarize_shap_values(values, ["attendance", "studytime"])
        self.assertEqual(result.iloc[0]["feature"], "studytime")
        self.assertAlmostEqual(result.iloc[0]["mean_abs_shap"], 0.6)
        self.assertAlmostEqual(result.iloc[1]["mean_shap"], 0.0666666667)

    def test_summary_rejects_misaligned_feature_names(self):
        with self.assertRaises(ValueError):
            summarize_shap_values(np.ones((3, 2)), ["only_one"])

    def test_summary_rejects_non_finite_values(self):
        with self.assertRaises(ValueError):
            summarize_shap_values(np.array([[np.nan]]), ["feature"])


if __name__ == "__main__":
    unittest.main()
