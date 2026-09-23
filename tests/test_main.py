from unittest.mock import patch
from main import main
import logging
def test_main_success(caplog):
    caplog.set_level(logging.INFO)

    fake_raw_data = [
    {
        "id": 123,
        "category": "burglary"
    }
    ]

    fake_cleaned_data = [
        {
            "id": 123,
            "category": "burglary",
            "latitude": 51.5,
            "longitude": -0.1,
            "street": "High Street",
            "month": "2026-01"
        }
    ]

    fake_env = {
        "POLICE_API_URL": "https://fake-api.com",
        "CRIME_DATE": "2026-01",
        "LATITUDE": "51.5",
        "LONGITUDE": "-0.1"
    }

    with patch.dict('os.environ', fake_env
                    ),patch('main.fetch_crime_data', return_value = fake_raw_data) as mock_fetch,patch(
                            'main.clean_records', return_value = fake_cleaned_data) as mock_clean,patch(
                            'main.save_json') as mock_save_json,patch(
                            'main.save_csv') as mock_save_csv: 
                    main()
    mock_fetch.assert_called_once_with(
        "https://fake-api.com",
        {
            "date": "2026-01",
            "lat": 51.5,
            "lng": -0.1
        }
    )
    mock_clean.assert_called_once_with(fake_raw_data)
    mock_save_json.assert_called_once()
    mock_save_csv.assert_called_once()
    assert 'Pipeline completed successfully' in caplog.text

def test_main_no_data(caplog):
    caplog.set_level(logging.INFO)

    fake_env = {
        "POLICE_API_URL": "https://fake-api.com",
        "CRIME_DATE": "2026-01",
        "LATITUDE": "51.5",
        "LONGITUDE": "-0.1"
    }

    with patch.dict('os.environ', fake_env), patch(
            'main.fetch_crime_data', return_value = []) as mock_fetch, patch(
            'main.clean_records', return_value=[]) as mock_clean, patch(
            'main.save_json') as mock_save_json,patch(
            'main.save_csv') as mock_save_csv : 
            main()
    mock_fetch.assert_called_once_with("https://fake-api.com",
            {
                "date": "2026-01",
                "lat": 51.5,
                "lng": -0.1
            })
    mock_clean.assert_called_once_with([])
    mock_save_json.assert_not_called()
    mock_save_csv.assert_not_called()
    assert 'No cleaned data available' in caplog.text