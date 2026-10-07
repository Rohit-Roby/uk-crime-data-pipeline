import pytest
from unittest.mock import patch, MagicMock

from orchestrate import get_crime_date


@patch("orchestrate.requests.get")
def test_get_crime_date_from_police_api(mock_get):
    mock_response = MagicMock()

    mock_response.json.return_value = {
        "date": "2026-08-01"
    }

    mock_get.return_value = mock_response

    result = get_crime_date()

    assert result == "2026-08"

    mock_get.assert_called_once_with(
        "https://data.police.uk/api/crime-last-updated",
        timeout=10
    )

    mock_response.raise_for_status.assert_called_once()


def test_get_crime_date_manual_override():
    result = get_crime_date(
        configured_date="2026-02"
    )

    assert result == "2026-02"


def test_get_crime_date_invalid_manual_override():
    with pytest.raises(
        ValueError,
        match="CRIME_DATE should use YYYY-MM format"
    ):
        get_crime_date(
            configured_date="2026-02-01"
        )