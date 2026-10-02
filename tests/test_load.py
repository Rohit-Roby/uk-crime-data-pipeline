import json
import csv
from load import save_json, save_csv, upload_to_gcs, load_gcs_csv_to_bigquery
from unittest.mock import patch, MagicMock

data = [{
        "id": 123,
        "category": "burglary",
        "latitude": 51.5
    },
    {
        "id": 456,
        "category": "vehicle-crime",
        "latitude": 52.1
    }]

def test_save_json(tmp_path):
    file_path = tmp_path/ 'test_data.json'

    save_json(data, file_path)

    assert file_path.exists()

    with open(file_path, 'r', encoding='utf-8') as file:
        saved_data = json.load(file)
    assert saved_data == data


def test_save_csv(tmp_path):
    file_path = tmp_path/ 'test_data.csv'

    save_csv(data,file_path)
    assert file_path.exists()

    with open(file_path, 'r', newline='', encoding='utf-8')as file:
        reader = csv.DictReader(file)
        saved_data = list(reader)

    assert len(saved_data) == len(data)
    assert saved_data[0]['category'] == 'burglary'
    assert float(saved_data[1]['latitude']) == 52.1

def test_save_csv_empty_data(tmp_path, caplog):
    file_path = tmp_path/ 'empty.csv'
    save_csv([], file_path)

    assert not file_path.exists()
    assert 'No data to save' in caplog.text

@patch("load.storage.Client")
def test_upload_to_gcs(mock_storage_client):
    mock_client = mock_storage_client.return_value
    mock_bucket = mock_client.bucket.return_value
    mock_blob = mock_bucket.blob.return_value

    local_file = "data/test.csv"
    bucket_name = "test_bucket"
    destination_blob = "cleaned/2026-01/test.csv"

    upload_to_gcs(local_file, bucket_name, destination_blob)

    mock_storage_client.assert_called_once_with()
    mock_client.bucket.asset_called_once_with(bucket_name)
    mock_bucket.blob.assert_called_once_with(destination_blob)
    mock_blob.upload_from_filename.assert_called_once_with(local_file)

@patch("load.bigquery.Client")
def test_load_gcs_csv_to_bigquery(mock_bigquery_client):
    mock_client = mock_bigquery_client.return_value
    mock_load_job = MagicMock()
    mock_client.load_table_from_uri.return_value = (
        mock_load_job
    )

    mock_table = MagicMock()
    mock_table.num_rows = 1648
    mock_client.get_table.return_value = mock_table

    load_gcs_csv_to_bigquery(
        bucket_id="test-bucket",
        blob_name="cleaned/2026-01/cleaned_crime_data.csv",
        project_id="test-project",
        dataset_id="crime_data",
        table_id="crimes_partitioned",
        location="europe-west2",
        crime_month="2026-01-01"
    )

    mock_bigquery_client.assert_called_once_with(
        project="test-project"
    )

    mock_client.load_table_from_uri.assert_called_once()

    mock_load_job.result.assert_called_once_with()

    mock_client.get_table.assert_called_once_with(
        "test-project.crime_data.crimes_partitioned$20260101"
    )
    args, kwargs = (
        mock_client.load_table_from_uri.call_args
    )

    assert args[0] == (
        "gs://test-bucket/"
        "cleaned/2026-01/"
        "cleaned_crime_data.csv"
    )

    assert args[1] == (
        "test-project."
        "crime_data."
        "crimes_partitioned$20260101"
    )

    assert kwargs["location"] == "europe-west2"
    job_config = kwargs["job_config"]
    assert (
        job_config.time_partitioning.field
        == "crime_month"
    )
    assert (
        job_config.write_disposition
        == "WRITE_TRUNCATE"
    )