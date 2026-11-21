from unittest.mock import Mock, patch

from src.research_ui import COUNTRIES, WORLD_BANK_INDICATORS, _latest_indicator


def test_country_catalogue_includes_multiple_regions():
    assert COUNTRIES["Pakistan"] == "PAK"
    assert COUNTRIES["Türkiye"] == "TUR"
    assert COUNTRIES["United Kingdom"] == "GBR"
    assert len(COUNTRIES) >= 15


def test_indicator_catalogue_uses_world_bank_series():
    assert WORLD_BANK_INDICATORS["Adult literacy (ages 15+)"][0] == "SE.ADT.LITR.ZS"
    assert "Tertiary education enrolment" in WORLD_BANK_INDICATORS


@patch("src.research_ui.requests.get")
def test_latest_indicator_returns_latest_non_null_observation(mock_get):
    response = Mock()
    response.json.return_value = [
        {"page": 1},
        [
            {"date": "2024", "value": None},
            {"date": "2023", "value": 72.5},
            {"date": "2022", "value": 70.0},
        ],
    ]
    response.raise_for_status.return_value = None
    mock_get.return_value = response

    result = _latest_indicator("PAK", "SE.ADT.LITR.ZS")

    assert result == {"value": 72.5, "year": "2023"}
    mock_get.assert_called_once()
