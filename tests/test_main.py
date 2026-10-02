from unittest.mock import patch, call
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
            "crime_month": "2026-01-01"
        }
    ]

    fake_env = {
        "POLICE_API_URL": "https://fake-api.com",
        "CRIME_DATE": "2026-01",
        "LATITUDE": "51.5",
        "LONGITUDE": "-0.1",
        "GCS_BUCKET_NAME": "test-bucket",
        "GCP_PROJECT_ID": "test-project",
        "GCP_REGION": "europe-west2",
        "BIGQUERY_DATASET": "crime_data",
        "BIGQUERY_TABLE": "crimes_partitioned"
    }

    with patch.dict('os.environ', fake_env
                    ),patch('main.fetch_crime_data', return_value = fake_raw_data) as mock_fetch,patch(
                            'main.clean_records', return_value = fake_cleaned_data) as mock_clean,patch(
                            'main.save_json') as mock_save_json,patch(
                            'main.save_csv') as mock_save_csv, patch(
                            "main.upload_to_gcs") as mock_upload, patch(
                            "main.load_gcs_csv_to_bigquery") as mock_bigquery: 
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
    assert mock_upload.call_count == 2
    mock_upload.assert_has_calls([
        call(
        "data/cleaned_crime_data.json",
        "test-bucket",
        "cleaned/2026-01/cleaned_crime_data.json"
        ),
        call(
            "data/cleaned_crime_data.csv",
            "test-bucket",
            "cleaned/2026-01/cleaned_crime_data.csv"
        )
    ])

    mock_bigquery.assert_called_once_with(
        bucket_id="test-bucket",
        blob_name=(
            "cleaned/2026-01/"
            "cleaned_crime_data.csv"
        ),
        project_id="test-project",
        dataset_id="crime_data",
        table_id="crimes_partitioned",
        location="europe-west2",
        crime_month="2026-01-01"
    )
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
            'main.save_csv') as mock_save_csv, patch(
            "main.upload_to_gcs") as mock_upload, patch(
            "main.load_gcs_csv_to_bigquery") as mock_bigquery : 
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
    mock_upload.assert_not_called()
    mock_bigquery.assert_not_called()
    assert 'No cleaned data available' in caplog.text

