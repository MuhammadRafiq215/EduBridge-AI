from unittest.mock import Mock, patch

from src.research_ui import WORLD_BANK_INDICATORS, _latest_indicator, _world_bank_countries


def test_country_catalogue_is_loaded_from_live_reporting_catalogue():
    payload = [
        {"page": 1},
        [
            {"id": "PAK", "name": "Pakistan", "region": {"value": "South Asia"}},
            {"id": "TUR", "name": "Türkiye", "region": {"value": "Europe & Central Asia"}},
            {"id": "GBR", "name": "United Kingdom", "region": {"value": "Europe & Central Asia"}},
            {"id": "WLD", "name": "World", "region": {"value": "Aggregates"}},
        ],
    ]
    response = Mock()
    response.json.return_value = payload
    response.raise_for_status.return_value = None
    with patch("src.research_ui.requests.get", return_value=response):
        _world_bank_countries.clear()
        countries = _world_bank_countries()
    assert countries == {"Pakistan": "PAK", "Türkiye": "TUR", "United Kingdom": "GBR"}
    _world_bank_countries.clear()


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
