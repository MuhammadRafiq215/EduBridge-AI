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


if __name__ == "__main__":
    unittest.main()
