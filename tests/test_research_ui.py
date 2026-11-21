import unittest
from unittest.mock import patch

from src import research_ui


class ResearchUITests(unittest.TestCase):
    def test_country_catalog_includes_reporting_countries_and_excludes_aggregates(self):
        class Response:
            def raise_for_status(self): pass
            def json(self):
                return [
                    {"pages": 1},
                    [
                        {"id": "PAK", "name": "Pakistan", "region": {"value": "South Asia"}},
                        {"id": "USA", "name": "United States", "region": {"value": "North America"}},
                        {"id": "WLD", "name": "World", "region": {"value": "Aggregates"}},
                    ],
                ]
        research_ui._world_bank_countries.clear()
        with patch("src.research_ui.requests.get", return_value=Response()):
            result = research_ui._world_bank_countries()
        self.assertEqual(result, {"Pakistan": "PAK", "United States": "USA"})
        research_ui._world_bank_countries.clear()

    def test_country_catalog_rejects_empty_or_unexpected_payload(self):
        class Response:
            def raise_for_status(self): pass
            def json(self): return [{"pages": 1}, []]
        research_ui._world_bank_countries.clear()
        with patch("src.research_ui.requests.get", return_value=Response()):
            with self.assertRaises(ValueError):
                research_ui._world_bank_countries()
        research_ui._world_bank_countries.clear()


if __name__ == "__main__":
    unittest.main()
